import numpy as np
from scipy.stats import beta, gamma, halfnorm, norm, logistic
import pandas as pd
import os
from scipy.optimize import minimize
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

from pybads import BADS


# ============================================================================
# Parameter Specifications (Bounds and Priors)
# ============================================================================
# Centralized definitions for both choice and confidence model parameters.
# Used by fitting infrastructure and model-specific modules.

# Choice model priors
DEFAULT_CHOICE_PRIORS: dict[str, tuple] = {
    "sens_noise": ("gamma", 1.75, 5.0),
    "sens_bias": ("normal", 0.0, 2.0),
    "p_lapse": ("beta", 1.0, 20.0),
}

# Confidence model priors
DEFAULT_CONF_PRIORS: dict[str, tuple] = {
    "pe_wt": ("normal", 0.0, 2),
    "pe_wt_v": ("normal", 0.0, 2),
    "bel_bias_v": ("normal", 0.0, 5),
    "bel_bias": ("normal", 0.0, 5),
    "pe_add": ("normal", 0.0, 5),
    "pe_add_v": ("normal", 0.0, 5),
    "sens_noise": ("gamma", 1.75, 5.0),
    "bel_noise": ("gamma", 1, 5.0),
    "sens_bias": ("normal", 0.0, 2),
    "p_lapse": ("beta", 1.0, 20.0),
}

# Confidence model parameter bounds (plb, pub, lower, upper, x0)
DEFAULT_CONF_PARAM_BOUNDS: dict[str, tuple[float, float, float, float, float]] = {
    "pe_wt": (np.arctanh(-0.5), np.arctanh(0.5), -5.0, 5.0, 0.0),
    "pe_wt_v": (np.arctanh(-0.5), np.arctanh(0.5), -5.0, 5.0, 0.0),
    "bel_bias_v": (-5, 5, -10.0, 10.0, 0.0),
    "bel_bias": (-5, 5, -10.0, 10.0, 0.0),
    "pe_add": (-5, 5, -10.0, 10.0, 0.0),
    "pe_add_v": (-5, 5, -10.0, 10.0, 0.0),
    "sens_noise": (0.01, 1.0, 0.0, 10.0, 0.5),
    "bel_noise": (0.01, 5.0, 0.0, 30.0, 0.5),
    "sens_bias": (-1.0, 1.0, -10.0, 10.0, 0.0),
    "p_lapse": (0.0, 0.1, 0.0, 0.5, 0.01),
    "mismatch_coef": (-0.5, 0.5, -1.0, 1.0, 0),
}

# Choice model parameter bounds (plb, pub, lower, upper, x0)
DEFAULT_CHOICE_PARAM_BOUNDS: dict[str, tuple[float, float, float, float, float]] = {
    "sens_noise": (1.0, 10.0, 0.5, 30.0, 1.0),
    "sens_bias": (-5.0, 5.0, -10.0, 10.0, 0.0),
    "p_lapse": (0.01, 0.05, 0.0, 0.1, 0.01),
}


def log_prior(pardict: dict, parnames: list[str], priors: dict) -> float:
    """Compute log prior over fitted parameters.

    Args:
        pardict: Parameter dict with all keys
        parnames: List of parameters being fitted
        priors: Dict mapping param names to (kind, *args) tuples
                kind in {normal, gamma, halfnormal, uniform, beta}

    Returns:
        Log prior density. -inf if out of support.
    """
    if not priors:
        return 0.0

    lp = 0.0
    for name in parnames:
        spec = priors.get(name)
        if spec is None:
            continue

        val = float(pardict[name])
        kind = spec[0]

        if kind == "normal":
            _, mu, sd = spec
            lp += float(norm.logpdf(val, loc=float(mu), scale=float(sd)))
        elif kind == "gamma":
            _, shape, scale = spec
            if val <= 0.0:
                return -np.inf
            lp += float(gamma.logpdf(val, a=float(shape), scale=float(scale)))
        elif kind == "halfnormal":
            _, scale = spec
            if val < 0.0:
                return -np.inf
            lp += float(halfnorm.logpdf(val, scale=float(scale)))
        elif kind == "uniform":
            _, lo, hi = spec
            if val < float(lo) or val > float(hi):
                return -np.inf
            lp += float(-np.log(float(hi) - float(lo)))
        elif kind == "beta":
            _, a, b = spec
            if val <= 0.0 or val >= 1.0:
                return -np.inf
            lp += float(beta.logpdf(val, a=float(a), b=float(b)))
        else:
            raise ValueError(f"Unknown prior kind {kind!r} for {name!r}")

    return -np.inf if not np.isfinite(lp) else lp


def draw_from_prior(spec: tuple, rng: np.random.Generator) -> float:
    """Sample one scalar from a prior spec ``(kind, *args)``.

    Mirrors the density dispatch in :func:`log_prior` (same ``kind`` values:
    normal, gamma, halfnormal, uniform, beta).
    """
    kind = spec[0]
    if kind == "normal":
        _, mu, sd = spec
        return float(rng.normal(float(mu), float(sd)))
    if kind == "gamma":
        _, shape, scale = spec
        return float(rng.gamma(float(shape), scale=float(scale)))
    if kind == "halfnormal":
        _, scale = spec
        return float(abs(rng.normal(0.0, float(scale))))
    if kind == "uniform":
        _, lo, hi = spec
        return float(rng.uniform(float(lo), float(hi)))
    if kind == "beta":
        _, a, b = spec
        return float(rng.beta(float(a), float(b)))
    raise ValueError(f"Unknown prior kind {kind!r}")


def _run_bads_once(opt_fun, x0, lb, ub, plb, pub, options):

    bads = BADS(opt_fun, x0, lb, ub, plb, pub, options=options)
    return bads.optimize()


def _format_fit_params(parnames: list[str], x: np.ndarray) -> str:
    if not parnames:
        return np.array2string(np.asarray(x, float).round(4), separator=", ")
    x = np.asarray(x, float).ravel()
    return ", ".join(f"{n}={v:.4g}" for n, v in zip(parnames, x))


def _cfg_for_restart(cfg: dict, restart_seed: int) -> dict:
    """Shallow cfg copy; only duplicate mc_rng when stochastic MC is enabled."""
    if not cfg.get("stochastic_mc"):
        return cfg
    cfg_i = dict(cfg)
    cfg_i["mc_rng"] = np.random.default_rng(restart_seed)
    return cfg_i


def _bads_restart_once(
    i: int,
    s: np.ndarray,
    *,
    df,
    cfg: dict,
    lb: np.ndarray,
    ub: np.ndarray,
    plb: np.ndarray,
    pub: np.ndarray,
    bads_options: dict,
    seed: int,
    myfun,
) -> dict:
    """Run one BADS restart; returns a picklable result dict."""
    restart_seed = int((seed + 97 * (i + 1)) % (2**31 - 1))
    cfg_i = _cfg_for_restart(cfg, restart_seed)
    run_options = dict(bads_options)
    run_options["random_seed"] = restart_seed

    def obj_i(x):
        x = np.asarray(x, float).ravel()
        ll = myfun(x, df, cfg_i)
        if not np.isfinite(ll):
            return 1e50
        return -float(ll)

    try:
        try:
            from threadpoolctl import threadpool_limits
        except ImportError:
            threadpool_limits = None

        if threadpool_limits is not None:
            with threadpool_limits(limits=1):
                res = _run_bads_once(obj_i, np.asarray(s, float), lb, ub, plb, pub, run_options)
        else:
            res = _run_bads_once(obj_i, np.asarray(s, float), lb, ub, plb, pub, run_options)
    except Exception as exc:
        return {
            "index": i,
            "success": False,
            "error": str(exc),
            "start": np.asarray(s, float),
        }

    x_hat = np.asarray(res["x"], float)
    ll_hat = -float(res["fval"])
    return {
        "index": i,
        "success": True,
        "x": x_hat,
        "ll": float(ll_hat) if np.isfinite(ll_hat) else -np.inf,
        "start": np.asarray(s, float),
        "func_count": int(res.get("func_count", 0)),
        "fval": float(res["fval"]),
        "fsd": float(res["fsd"]) if "fsd" in res else None,
    }


def _lbfgs_restart_once(
    i: int,
    s: np.ndarray,
    *,
    df,
    cfg: dict,
    bounds: list,
    lbfgs_options: dict,
    seed: int,
    myfun,
) -> dict:
    """Run one L-BFGS-B restart; returns a picklable result dict."""
    restart_seed = int((seed + 97 * (i + 1)) % (2**31 - 1))
    cfg_i = _cfg_for_restart(cfg, restart_seed)

    def obj_i(x):
        x = np.asarray(x, float).ravel()
        ll = myfun(x, df, cfg_i)
        if not np.isfinite(ll):
            return 1e50
        return -float(ll)

    try:
        try:
            from threadpoolctl import threadpool_limits
        except ImportError:
            threadpool_limits = None

        if threadpool_limits is not None:
            with threadpool_limits(limits=1):
                res = minimize(obj_i, np.asarray(s, float), method="L-BFGS-B", bounds=bounds, options=lbfgs_options)
        else:
            res = minimize(obj_i, np.asarray(s, float), method="L-BFGS-B", bounds=bounds, options=lbfgs_options)
    except Exception as exc:
        return {
            "index": i,
            "success": False,
            "error": str(exc),
            "start": np.asarray(s, float),
        }

    x_hat = np.asarray(res.x, float)
    ll_hat = myfun(x_hat, df, cfg_i)
    return {
        "index": i,
        "success": True,
        "x": x_hat,
        "ll": float(ll_hat) if np.isfinite(ll_hat) else -np.inf,
        "start": np.asarray(s, float),
        "nfev": int(res.nfev),
        "nit": int(res.nit),
        "fun": float(res.fun),
        "message": str(res.message),
        "scipy_success": bool(res.success),
    }


def _restart_process_worker(payload: dict) -> dict:
    """Process-pool entry point (module-level for pickling), shared by BADS/LBFGS.

    ``payload["kind"]`` selects the single-restart function; ``myfun`` travels
    in the payload (module-level callables pickle by reference).
    """
    if payload["kind"] == "bads":
        return _bads_restart_once(
            payload["index"],
            np.asarray(payload["start"], float),
            df=payload["df"],
            cfg=payload["cfg"],
            lb=np.asarray(payload["lb"], float),
            ub=np.asarray(payload["ub"], float),
            plb=np.asarray(payload["plb"], float),
            pub=np.asarray(payload["pub"], float),
            bads_options=payload["bads_options"],
            seed=int(payload["seed"]),
            myfun=payload["myfun"],
        )
    return _lbfgs_restart_once(
        payload["index"],
        np.asarray(payload["start"], float),
        df=payload["df"],
        cfg=payload["cfg"],
        bounds=payload["bounds"],
        lbfgs_options=payload["lbfgs_options"],
        seed=int(payload["seed"]),
        myfun=payload["myfun"],
    )


def _build_restart_starts(
    n_restarts: int,
    *,
    x0: np.ndarray,
    lb: np.ndarray,
    ub: np.ndarray,
    plb: np.ndarray,
    pub: np.ndarray,
    use_x0: bool,
    rng: np.random.Generator,
) -> list[np.ndarray]:
    """First start is ``x0`` (if ``use_x0``); remaining starts uniform in ``[plb, pub]``."""
    n_starts_req = max(1, int(n_restarts))
    if use_x0:
        starts = [np.clip(x0, lb, ub)]
        for _ in range(max(0, n_starts_req - 1)):
            starts.append(np.clip(rng.uniform(plb, pub), lb, ub))
    else:
        starts = [np.clip(rng.uniform(plb, pub), lb, ub) for _ in range(n_starts_req)]
    return starts


def _run_restarts(
    starts: list[np.ndarray],
    *,
    kind: str,
    run_one,
    payload_extra: dict,
    n_jobs: int,
    parallel_backend: str,
    verbose: bool,
    prefix: str,
    parnames: list[str],
    label: str,
) -> list[dict]:
    """Run all restarts (serial / thread / process), return results sorted by index.

    ``run_one(i, s) -> dict`` executes one restart in-process (used for serial
    and thread backends). ``payload_extra`` carries whatever ``run_one``'s
    process-pool counterpart (:func:`_restart_process_worker`) needs to
    reconstruct the call in a subprocess; ``kind`` selects which single-restart
    function that worker dispatches to.
    """
    n_starts = len(starts)
    backend = str(parallel_backend).lower().strip()
    use_parallel = n_jobs != 1 and n_starts > 1 and backend != "serial"
    if use_parallel:
        max_workers = min(n_starts, os.cpu_count() or 1) if n_jobs < 0 else min(int(n_jobs), n_starts)
    else:
        max_workers = 1

    results: list[dict] = []
    live_verbose = False
    if not use_parallel or backend == "serial":
        results = [run_one(i, s) for i, s in enumerate(starts)]
    elif backend == "thread":
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {executor.submit(run_one, i, s): i for i, s in enumerate(starts)}
            for future in as_completed(future_map):
                i = future_map[future]
                try:
                    results.append(future.result())
                except Exception as exc:
                    results.append({"index": i, "success": False, "error": str(exc), "start": starts[i]})
    else:
        payloads = [
            {"index": i, "start": np.asarray(s, float), "kind": kind, **payload_extra}
            for i, s in enumerate(starts)
        ]
        parallel_failed = False
        try:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                future_map = {
                    executor.submit(_restart_process_worker, payload): payload["index"]
                    for payload in payloads
                }
                for future in as_completed(future_map):
                    i = future_map[future]
                    try:
                        out = future.result()
                        results.append(out)
                        if verbose:
                            live_verbose = True
                            tag = f"{prefix}  {label} restart {out['index']}:"
                            if out.get("success"):
                                print(f"{tag} ll={out['ll']:.2f}  {_format_fit_params(parnames, out['x'])}")
                            else:
                                print(f"{tag} FAILED ({out.get('error', 'unknown error')})")
                    except Exception as exc:
                        results.append({"index": i, "success": False, "error": str(exc), "start": starts[i]})
        except (PermissionError, OSError, RuntimeError):
            parallel_failed = True
        if parallel_failed:
            if verbose:
                print(f"{prefix}  {label} process pool failed; falling back to serial restarts.")
            results = [run_one(i, s) for i, s in enumerate(starts)]

    results.sort(key=lambda r: r["index"])

    if verbose and not live_verbose:
        for r in results:
            tag = f"{prefix}  {label} restart {r['index']}:"
            if r.get("success"):
                print(f"{tag} ll={r['ll']:.2f}  {_format_fit_params(parnames, r['x'])}")
            else:
                print(f"{tag} FAILED ({r.get('error', 'unknown error')})")

    return results


def fit_model_BADS(
    modelinfo,
    df,
    options=None,
    n_restarts=10,
    seed=0,
    n_jobs=-1,
    *,
    use_x0: bool = True,
    parallel_backend: str = "process",
):
    """
    Bayesian Adaptive Direct Search (pyBADS) for noisy / nonsmooth objectives.

    Expects the same ``modelinfo`` fields as :func:`fit_model_LBFGS`. Minimizes
    negative log-likelihood. With ``uncertainty_handling=True`` (default), BADS
    treats the objective as stochastic (e.g. when ``cfg["stochastic_mc"]`` is set).

    Runs ``n_restarts`` optimizations. By default the first start is ``x0`` and
    the rest are uniform in ``[plb, pub]``. With ``use_x0=False``, all starts
    are random in ``[plb, pub]``. Restarts run in parallel when ``n_jobs != 1``
    (default backend ``process``: one BADS job per worker with BLAS pinned to
    1 thread; ``thread`` uses ``ThreadPoolExecutor``; ``serial`` forces one worker).
    Each restart uses its own ``mc_rng`` when ``cfg["stochastic_mc"]`` is set.

    Optional ``modelinfo`` keys: ``verbose`` (default True), ``print_prefix``.

    Returns:
      (best_x, best_ll, info)
    """
    rng = np.random.default_rng(seed)

    lb, ub = modelinfo["bounds"]
    lb = np.asarray(lb, float)
    ub = np.asarray(ub, float)
    plb = np.asarray(modelinfo["plb"], float)
    pub = np.asarray(modelinfo["pub"], float)

    x0 = np.asarray(modelinfo["x0"], float)
    myfun = modelinfo["myfun"]
    cfg = modelinfo["cfg"]
    parnames = list(cfg.get("parnames", []))
    verbose = bool(modelinfo.get("verbose", True))
    prefix = str(modelinfo.get("print_prefix", ""))

    bads_options = {
        "uncertainty_handling": bool(cfg.get("stochastic_mc", False)),
        "max_fun_evals": 500,
        "display": "off",
        "noise_final_samples": 20,
        "random_seed": int(seed),
    }
    if modelinfo.get("options"):
        bads_options.update(modelinfo["options"])
    if options:
        bads_options.update(options)

    starts = _build_restart_starts(
        n_restarts, x0=x0, lb=lb, ub=ub, plb=plb, pub=pub, use_x0=use_x0, rng=rng
    )

    def _run_restart(i: int, s: np.ndarray) -> dict:
        out = _bads_restart_once(
            i, s, df=df, cfg=cfg, lb=lb, ub=ub, plb=plb, pub=pub,
            bads_options=bads_options, seed=seed, myfun=myfun,
        )
        if out.get("success"):
            out = dict(out)
            out["res"] = {
                "x": out["x"],
                "fval": out["fval"],
                "func_count": out.get("func_count", 0),
                "fsd": out.get("fsd"),
            }
        return out

    results = _run_restarts(
        starts,
        kind="bads",
        run_one=_run_restart,
        payload_extra={
            "df": df, "cfg": cfg, "lb": lb, "ub": ub, "plb": plb, "pub": pub,
            "bads_options": bads_options, "seed": int(seed), "myfun": myfun,
        },
        n_jobs=n_jobs,
        parallel_backend=parallel_backend,
        verbose=verbose,
        prefix=prefix,
        parnames=parnames,
        label="BADS",
    )
    # The process-pool path returns raw _bads_restart_once dicts without "res";
    # backfill it here so downstream code can rely on it uniformly.
    for out in results:
        if out.get("success") and "res" not in out:
            out["res"] = {
                "x": out["x"],
                "fval": out["fval"],
                "func_count": out.get("func_count", 0),
                "fsd": out.get("fsd"),
            }

    ok = [r for r in results if r.get("success") and np.isfinite(r.get("ll", -np.inf))]
    if not ok:
        best_x = np.clip(x0, lb, ub)
        cfg_fallback = _cfg_for_restart(cfg, int(seed))
        ll_direct = myfun(best_x, df, cfg_fallback)
        best_ll = float(ll_direct) if np.isfinite(ll_direct) else -np.inf
        if verbose:
            print(
                f"{prefix}  BADS best: all restarts failed; "
                f"fallback ll={best_ll:.2f}  {_format_fit_params(parnames, best_x)}"
            )
        info = {
            "success": False,
            "message": "All BADS restarts failed",
            "func_count": None,
            "fval": -best_ll if np.isfinite(best_ll) else None,
            "n_restarts": len(starts),
            "restart_results": results,
        }
        return best_x, best_ll, info

    best = max(ok, key=lambda r: r["ll"])
    best_x = best["x"]
    best_ll = best["ll"]
    best_res = best["res"]

    if verbose:
        print(
            f"{prefix}  BADS best (restart {best['index']}): "
            f"ll={best_ll:.2f}  {_format_fit_params(parnames, best_x)}"
        )

    info = {
        "success": True,
        "message": "BADS finished",
        "func_count": int(best_res.get("func_count", 0)),
        "fval": float(best_res["fval"]),
        "fsd": float(best_res["fsd"]) if "fsd" in best_res else None,
        "n_restarts": len(starts),
        "best_restart": int(best["index"]),
        "all_ll": [r.get("ll") for r in results],
        "restart_results": results,
    }
    return best_x, best_ll, info

def fit_model_LBFGS(
    modelinfo,
    df,
    options=None,
    n_restarts=10,
    seed=0,
    n_jobs=-1,
    *,
    use_x0: bool = True,
    parallel_backend: str = "process",
):
    """
    scipy L-BFGS-B over random restarts; fast alternative to fit_model_BADS
    for smooth/deterministic objectives, parallelized the same way.

    Expects the same ``modelinfo`` fields as :func:`fit_model_BADS`.

    Runs ``n_restarts`` optimizations. By default the first start is ``x0`` and
    the rest are uniform in ``[plb, pub]`` (falls back to ``[lb, ub]`` if
    ``plb``/``pub`` are absent). With ``use_x0=False``, all starts are random.
    Restarts run in parallel when ``n_jobs != 1`` (default backend ``process``:
    one L-BFGS-B run per worker with BLAS pinned to 1 thread; ``thread`` uses
    ``ThreadPoolExecutor``; ``serial`` forces one worker).

    Optional ``modelinfo`` keys: ``verbose`` (default True), ``print_prefix``.

    Returns:
      (best_x, best_ll, info)
    """
    if options is None:
        options = {}

    rng = np.random.default_rng(seed)

    lb, ub = modelinfo["bounds"]
    lb = np.asarray(lb, float)
    ub = np.asarray(ub, float)
    bounds = list(zip(lb, ub))
    if "plb" in modelinfo and "pub" in modelinfo:
        plb = np.asarray(modelinfo["plb"], float)
        pub = np.asarray(modelinfo["pub"], float)
    else:
        plb, pub = lb, ub

    x0 = np.asarray(modelinfo["x0"], float)
    myfun = modelinfo["myfun"]
    cfg = modelinfo["cfg"]
    parnames = list(cfg.get("parnames", []))
    verbose = bool(modelinfo.get("verbose", True))
    prefix = str(modelinfo.get("print_prefix", ""))

    lbfgs_options = {
        "maxiter": int(options.get("maxiter", 200)),
        "ftol": float(options.get("ftol", 1e-9)),
    }

    starts = _build_restart_starts(
        n_restarts, x0=x0, lb=lb, ub=ub, plb=plb, pub=pub, use_x0=use_x0, rng=rng
    )

    def _run_restart(i: int, s: np.ndarray) -> dict:
        return _lbfgs_restart_once(
            i, s, df=df, cfg=cfg, bounds=bounds, lbfgs_options=lbfgs_options, seed=seed, myfun=myfun
        )

    results = _run_restarts(
        starts,
        kind="lbfgs",
        run_one=_run_restart,
        payload_extra={
            "df": df, "cfg": cfg, "bounds": bounds,
            "lbfgs_options": lbfgs_options, "seed": int(seed), "myfun": myfun,
        },
        n_jobs=n_jobs,
        parallel_backend=parallel_backend,
        verbose=verbose,
        prefix=prefix,
        parnames=parnames,
        label="LBFGS",
    )

    ok = [r for r in results if r.get("success") and np.isfinite(r.get("ll", -np.inf))]
    if not ok:
        best_x = np.clip(x0, lb, ub)
        ll_direct = myfun(best_x, df, cfg)
        best_ll = float(ll_direct) if np.isfinite(ll_direct) else -np.inf
        if verbose:
            print(
                f"{prefix}  LBFGS best: all restarts failed; "
                f"fallback ll={best_ll:.2f}  {_format_fit_params(parnames, best_x)}"
            )
        info = {
            "success": False,
            "message": "All LBFGS restarts failed",
            "n_restarts": len(starts),
            "best_restart": None,
            "all_ll": [r.get("ll") for r in results],
            "restart_results": results,
        }
        return best_x, best_ll, info

    best = max(ok, key=lambda r: r["ll"])
    best_x = best["x"]
    best_ll = best["ll"]

    if verbose:
        print(
            f"{prefix}  LBFGS best (restart {best['index']}): "
            f"ll={best_ll:.2f}  {_format_fit_params(parnames, best_x)}"
        )

    info = {
        "success": bool(best.get("scipy_success", False)),
        "message": best.get("message", ""),
        "nfev": best.get("nfev"),
        "nit": best.get("nit"),
        "fun": best.get("fun"),
        "n_restarts": len(starts),
        "best_restart": int(best["index"]),
        "all_ll": [r.get("ll") for r in results],
        "restart_results": results,
    }
    return best_x, best_ll, info
