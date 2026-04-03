
import numpy as np
from scipy.stats import norm,logistic
import pandas as pd
import os
from scipy.optimize import minimize
from concurrent.futures import ThreadPoolExecutor, as_completed


def psychofun(theta,stim, pd = 'normal'):
    """Psychometric function based on logistic/normal CDF and lapses"""
    
    if pd == 'logistic':
        dist = logistic
    elif pd == 'normal':
        dist = norm
        
    mu = theta[0]          # bias
    sigma = theta[1]       # slope/noise
    lapse = theta[2]       # lapse rate
    if len(theta) == 4:    # lapse bias
        lapse_bias = theta[3];
    else:
        lapse_bias = 0.5   # if theta has only three elements, assume symmetric lapses
    
    p_right = dist.cdf(stim,loc=-mu,scale=sigma)    # Probability of responding "rightwards", without lapses
    p_right = lapse*lapse_bias + (1-lapse)*p_right # Adding lapses

    return p_right

def psychofun_inv(theta,p_right, pd= 'normal'):
    
    """Psychometric function based on logistic/normal CDF and lapses"""

    if pd == 'logistic':
        dist = logistic
    elif pd == 'normal':
        dist = norm
        
    mu = theta[0]          # bias
    sigma = theta[1]       # slope/noise
    lapse = theta[2]       # lapse rate
    if len(theta) == 4:    # lapse bias
        lapse_bias = theta[3];
    else:
        lapse_bias = 0.5   # if theta has only three elements, assume symmetric lapses
    
    # p_right = norm.cdf(stim,loc=mu,scale=sigma)    # Probability of responding "rightwards", without lapses
    # p_right = lapse*lapse_bias + (1-lapse)*p_right # Adding lapses
    p_right_prime = (p_right-lapse*lapse_bias)/(1-lapse)    
    stim = dist.ppf(p_right_prime,loc=mu,scale = sigma)
    
    return stim

def psychofun_ll(params,df,cfg,stimcol='stim',choicecol='a'):
    stim= np.array([df[stimcol]])
    a = np.array(df[choicecol])
    # conf = np.array(df['conf'])
    pardict = {}
    for npar, ipar in enumerate(cfg['parnames']):
        pardict[ipar] = params[npar]

    for key,value in cfg['fixedpars'].items():
        pardict[key] = value
    sigma_act = pardict.get('sigma_act', 0)
    choice_bias = pardict.get('choice_bias', 0)
    lapse = pardict.get('lapse', 0)
    
    stim = np.array(stim,dtype=float)
    ntrials = stim.shape[1]

    pRight = norm.cdf(stim+choice_bias,0,np.sqrt(2*sigma_act**2))
    pRight = lapse*0.5 + (1-lapse)*pRight
    pA = pRight*(a==1)+(1-pRight)*(a==-1)
    pA = pA.clip(1e-10,1-1e-10)
    ll = np.nansum(np.log(pA))
    return ll

def fit_model_LBFGS(modelinfo, df, options=None, n_restarts=5, seed=0):
    """
    Fast alternative to fit_model_BADS using scipy L-BFGS-B.

    Expects modelinfo fields like your code:
      - modelinfo['x0'] : initial guess list
      - modelinfo['bounds'] : [lb_list, ub_list]
      - modelinfo['myfun'] : log-likelihood function to maximize
      - modelinfo['cfg'] : cfg dict passed into myfun
      - modelinfo['options'] : unused here, kept for compatibility

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

    x0 = np.asarray(modelinfo["x0"], float)
    myfun = modelinfo["myfun"]
    cfg = modelinfo["cfg"]

    # objective for scipy (minimize negative log-likelihood)
    def obj(x):
        ll = myfun(x, df, cfg)
        if not np.isfinite(ll):
            return 1e50
        return -ll

    # generate starting points: x0 + random points in box (biased to plausible range if provided)
    starts = [x0]

    # If you have "plb/pub" (plausible bounds), sample there for restarts
    if "plb" in modelinfo and "pub" in modelinfo:
        plb = np.asarray(modelinfo["plb"], float)
        pub = np.asarray(modelinfo["pub"], float)
        for _ in range(max(0, n_restarts - 1)):
            starts.append(rng.uniform(plb, pub))
    else:
        for _ in range(max(0, n_restarts - 1)):
            starts.append(rng.uniform(lb, ub))

    best_x = None
    best_ll = -np.inf
    best_res = None

    for s in starts:
        s = np.clip(np.asarray(s, float), lb, ub)
        res = minimize(
            obj,
            s,
            method="L-BFGS-B",
            bounds=bounds,
            options={
                "maxiter": int(options.get("maxiter", 200)),
                "ftol": float(options.get("ftol", 1e-9)),
            },
        )

        x_hat = res.x
        ll_hat = myfun(x_hat, df, cfg)

        if np.isfinite(ll_hat) and ll_hat > best_ll:
            best_ll = float(ll_hat)
            best_x = np.array(x_hat, float)
            best_res = res

    info = {
        "success": bool(best_res.success) if best_res is not None else False,
        "message": best_res.message if best_res is not None else "No result",
        "nfev": int(best_res.nfev) if best_res is not None else None,
        "nit": int(best_res.nit) if best_res is not None else None,
        "fun": float(best_res.fun) if best_res is not None else None,  # negative ll at optimum
    }
    return best_x, best_ll, info

def fit_model_LBFGS_parallel(
    modelinfo,
    df,
    options=None,
    n_restarts=10,
    seed=0,
    n_jobs=-1,
    backend="loky",   # "loky" (process) | "threading"
):
    """
    Parallel L-BFGS-B over random restarts.

    Returns:
      best_x, best_ll, info
    """
    if options is None:
        options = {}

    lb, ub = modelinfo["bounds"]
    lb = np.asarray(lb, float)
    ub = np.asarray(ub, float)
    bounds = list(zip(lb, ub))

    x0 = np.asarray(modelinfo["x0"], float)
    myfun = modelinfo["myfun"]
    cfg = modelinfo["cfg"]

    rng = np.random.default_rng(seed)

    # Build start points (x0 + random starts from plausible bounds if provided)
    if n_restarts < 2:
        starts = [np.clip(x0, lb, ub)]
    if n_restarts > 1:
        starts = []
        if "plb" in modelinfo and "pub" in modelinfo:
            plb = np.asarray(modelinfo["plb"], float)
            pub = np.asarray(modelinfo["pub"], float)
            for _ in range(n_restarts - 1):
                starts.append(np.clip(rng.uniform(plb, pub), lb, ub))
        else:
            for _ in range(n_restarts - 1):
                starts.append(rng.uniform(lb, ub))

    maxiter = int(options.get("maxiter", 300))
    ftol = float(options.get("ftol", 1e-9))

    # Worker: run one restart
    def _one_start(s):
        # print("PID", os.getpid()) #debug: should see different PIDs

        s = np.asarray(s, float)

        def obj(x):
            ll = myfun(x, df, cfg)
            if not np.isfinite(ll):
                return 1e50
            return -ll

        res = minimize(
            obj,
            s,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": maxiter, "ftol": ftol},
        )

        x_hat = np.asarray(res.x, float)
        ll_hat = myfun(x_hat, df, cfg)
        return {
            "x": x_hat,
            "ll": float(ll_hat) if np.isfinite(ll_hat) else -np.inf,
            "success": bool(res.success),
            "message": str(res.message),
            "nfev": int(res.nfev),
            "nit": int(res.nit),
            "fun": float(res.fun),
        }

    # Run in parallel if joblib is available and n_jobs != 1
    results = None
    if n_jobs == 1 or len(starts) == 1:
        results = [_one_start(s) for s in starts]
    else:
        try:
            from joblib import Parallel, delayed
            results = Parallel(n_jobs=n_jobs, backend=backend)(
                delayed(_one_start)(s) for s in starts
            )
        except Exception:
            # fallback: sequential
            results = [_one_start(s) for s in starts]

    # Pick best
    best = max(results, key=lambda d: d["ll"])
    info = {
        "n_starts": len(starts),
        "best_success": best["success"],
        "best_message": best["message"],
        "best_nfev": best["nfev"],
        "best_nit": best["nit"],
        "best_fun": best["fun"],  # negative LL at optimum
        "all_ll": [r["ll"] for r in results],
        "all_success": [r["success"] for r in results],
    }
    return best["x"], best["ll"], info
