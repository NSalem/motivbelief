#!/usr/bin/env Rscript
#
# LEGACY — hierarchical group-level hmetad (diverged on exp1a; do not use for paper).
# Primary entrypoint: scripts/r/fit_hmeta_d.R (per-participant Bayesian fits).
# MLE legacy: python scripts/_old/fit_hmeta_d_mle.py
#
# Usage:
#   Rscript scripts/r/_old/fit_hmeta_d_hierarchical.R --dataset exp1a
#
# Datasets (Free only):
#   exp1a, exp1b, exp2, merged (exp1a+exp2), sim_act, sim_intent, sim_confirm
#
# Outputs under results/hmeta_d/<dataset>/ (same layout as when this was primary).

# Progress to stderr (usually unbuffered under Rscript; cat to stdout can sit silent).
progress <- function(...) {
  msg <- paste0(...)
  cat(msg, "\n", file = stderr(), sep = "")
  flush(stderr())
  invisible(NULL)
}

progress(sprintf("[%s] fit_hmeta_d.R starting (loading R packages; can take ~30–90s)...",
                 format(Sys.time(), "%H:%M:%S")))
suppressPackageStartupMessages({
  library(hmetad)
  library(brms)
  library(posterior)
  library(dplyr)
  library(tidyr)
  library(jsonlite)
})
progress(sprintf("[%s] packages loaded", format(Sys.time(), "%H:%M:%S")))

# ---- CLI -----------------------------------------------------------------

REAL_DATASETS <- c("exp1a", "exp1b", "exp2")
MERGED_DATASETS <- c("merged")  # Free trials pooled from exp1a + exp2
SIM_DATASETS <- c("sim_act")
ALL_DATASETS <- c(REAL_DATASETS, MERGED_DATASETS, SIM_DATASETS)
SIM_FILES <- c(sim_act = "sims_act.csv")

parse_args <- function(argv) {
  opts <- list(
    dataset = NULL,
    all = FALSE,
    out_root = "results/hmeta_d",
    repo_root = NULL,
    n_ratings = 6L,
    chains = 4L,
    cores = NULL,  # default: min(chains, detectCores())
    iter = 6000L,
    warmup = 2000L,
    criteria_mode = "default",
    seed = 1L,
    empty = FALSE,
    max_subjects = NULL,
    help = FALSE
  )
  i <- 1L
  while (i <= length(argv)) {
    a <- argv[[i]]
    if (a %in% c("-h", "--help")) {
      opts$help <- TRUE
    } else if (a == "--all") {
      opts$all <- TRUE
    } else if (a == "--empty") {
      opts$empty <- TRUE
    } else if (a == "--dataset") {
      i <- i + 1L; opts$dataset <- argv[[i]]
    } else if (a == "--out-root") {
      i <- i + 1L; opts$out_root <- argv[[i]]
    } else if (a == "--repo-root") {
      i <- i + 1L; opts$repo_root <- argv[[i]]
    } else if (a == "--n-ratings") {
      i <- i + 1L; opts$n_ratings <- as.integer(argv[[i]])
    } else if (a == "--chains") {
      i <- i + 1L; opts$chains <- as.integer(argv[[i]])
    } else if (a == "--cores") {
      i <- i + 1L; opts$cores <- as.integer(argv[[i]])
    } else if (a == "--iter") {
      i <- i + 1L; opts$iter <- as.integer(argv[[i]])
    } else if (a == "--warmup") {
      i <- i + 1L; opts$warmup <- as.integer(argv[[i]])
    } else if (a == "--criteria-mode") {
      i <- i + 1L; opts$criteria_mode <- argv[[i]]
    } else if (a == "--seed") {
      i <- i + 1L; opts$seed <- as.integer(argv[[i]])
    } else if (a == "--max-subjects") {
      i <- i + 1L; opts$max_subjects <- as.integer(argv[[i]])
    } else {
      stop("Unknown argument: ", a, call. = FALSE)
    }
    i <- i + 1L
  }
  opts
}

print_help <- function() {
  cat(paste(
    "Fit hierarchical meta-d' (coh x incentive) with CRAN hmetad.",
    "",
    "Usage:",
    "  Rscript scripts/r/fit_hmeta_d.R --dataset exp1a",
    "  Rscript scripts/r/fit_hmeta_d.R --all",
    "",
    "Options:",
    "  --dataset NAME       One of: exp1a, exp1b, exp2, merged, sim_act, sim_intent, sim_confirm",
    "  --all                Fit all datasets",
    "  --out-root DIR       Output root (default: results/hmeta_d)",
    "  --repo-root DIR      Repository root (default: auto from script path)",
    "  --n-ratings K        Ordinal confidence bins (default: 6)",
    "  --chains N           MCMC chains (default: 4)",
    "  --cores N            Parallel cores for chains (default: min(chains, detectCores()))",
    "  --iter N             Total iterations per chain (default: 2000)",
    "  --warmup N           Warmup iterations (default: 1000)",
    "  --criteria-mode M    default | shared (default: default)",
    "                       default: mu~inc*coh3; d'~coh3; c~1; type2~inc",
    "                       (uncorrelated REs; no subject-level inc×coh3)",
    "                       shared:  same but type2 criteria ~1 only",
    "  --seed N             RNG seed (default: 1)",
    "  --max-subjects N     Cap subjects (smoke tests)",
    "  --empty              Build model without MCMC",
    "  -h, --help           Show this help",
    sep = "\n"
  ), "\n")
}

# Normalize mode name; 'full' kept as deprecated alias of 'default'.
normalize_criteria_mode <- function(mode) {
  if (identical(mode, "full")) {
    progress("NOTE: --criteria-mode full is deprecated; using 'default' structure.")
    return("default")
  }
  mode
}

#' Build brms/hmetad formulas for a criteria mode.
#'
#' Predictors: incentive (factor), coh3 (ordered numeric -1/0/+1).
#' Random effects are uncorrelated (||). Population keeps incentive * coh3;
#' subject-level interaction slope is omitted.
#'
#' default:
#'   mu (log M-ratio) ~ incentive * coh3 + (1 + incentive + coh3 || participant)
#'   dprime             ~ coh3 + (1 + coh3 || participant)
#'   c (type-1 bias)    ~ 1 + (1 | participant)
#'   type-2 diffs       ~ incentive + (1 | participant)
#'
#' shared: same, but type-2 diffs ~ 1 + (1 | participant)
build_metad_formula <- function(criteria_mode, K) {
  mc <- metac2_parameters(K = K)
  t2 <- paste(mc, collapse = " + ")

  if (criteria_mode == "default") {
    f <- bf(
      N ~ incentive * coh3 + (1 + incentive + coh3 || participant),
      dprime ~ coh3 + (1 + coh3 || participant),
      c ~ 1 + (1 | participant),
      as.formula(paste(t2, "~ incentive + (1 | participant)"))
    )
  } else if (criteria_mode == "shared") {
    f <- bf(
      N ~ incentive * coh3 + (1 + incentive + coh3 || participant),
      dprime ~ coh3 + (1 + coh3 || participant),
      c ~ 1 + (1 | participant),
      as.formula(paste(t2, "~ 1 + (1 | participant)"))
    )
  } else {
    stop("criteria_mode must be 'default' or 'shared' (got ", criteria_mode, ")",
         call. = FALSE)
  }
  f
}

# ---- Paths / backend -----------------------------------------------------

find_repo_root <- function(cli_root = NULL) {
  if (!is.null(cli_root) && nzchar(cli_root)) {
    return(normalizePath(cli_root, mustWork = TRUE))
  }
  # Rscript: scripts/r/_old/fit_hmeta_d_hierarchical.R -> repo root is three levels up
  script <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE))
  if (length(script) && nzchar(script[[1]])) {
    cand <- normalizePath(file.path(dirname(script[[1]]), "..", "..", ".."), mustWork = FALSE)
    if (dir.exists(file.path(cand, "data")) && dir.exists(file.path(cand, "scripts"))) {
      return(cand)
    }
  }
  # RStudio / interactive: walk up from getwd()
  wd <- normalizePath(getwd(), mustWork = TRUE)
  cur <- wd
  for (i in seq_len(6L)) {
    if (dir.exists(file.path(cur, "data")) && dir.exists(file.path(cur, "scripts", "r"))) {
      return(cur)
    }
    parent <- dirname(cur)
    if (identical(parent, cur)) break
    cur <- parent
  }
  wd
}

#' Run one or more hmetad fits (safe to call from RStudio).
#'
#' @examples
#' run_fit_hmeta_d(dataset = "exp1a", empty = TRUE, max_subjects = 3L,
#'                 criteria_mode = "shared")
resolve_cores <- function(cores, chains) {
  n_chains <- as.integer(chains)
  if (is.null(cores) || is.na(cores)) {
    n_avail <- parallel::detectCores()
    if (is.na(n_avail) || n_avail < 1L) n_avail <- 1L
    cores <- min(n_chains, n_avail)
  }
  as.integer(max(1L, cores))
}

run_fit_hmeta_d <- function(
    dataset = NULL,
    all = FALSE,
    out_root = "results/hmeta_d",
    repo_root = NULL,
    n_ratings = 6L,
    chains = 4L,
    cores = NULL,
    iter = 2000L,
    warmup = 1000L,
    criteria_mode = "default",
    seed = 1L,
    empty = FALSE,
    max_subjects = NULL
) {
  if (!all && is.null(dataset)) {
    stop("Pass dataset = \"exp1a\" (etc.) or all = TRUE", call. = FALSE)
  }
  if (!is.null(dataset) && !dataset %in% ALL_DATASETS) {
    stop("Unknown dataset; choose from: ", paste(ALL_DATASETS, collapse = ", "), call. = FALSE)
  }
  criteria_mode <- normalize_criteria_mode(criteria_mode)
  if (!criteria_mode %in% c("default", "shared")) {
    stop("criteria_mode must be 'default' or 'shared'", call. = FALSE)
  }

  repo_root <- find_repo_root(repo_root)
  out_root_abs <- if (grepl("^(/|[A-Za-z]:)", out_root)) {
    out_root
  } else {
    file.path(repo_root, out_root)
  }
  progress("repo_root: ", repo_root)
  progress("out_root: ", out_root_abs)
  backend <- setup_backend()
  datasets <- if (all) ALL_DATASETS else dataset
  n_cores <- resolve_cores(cores, chains)
  progress("datasets: ", paste(datasets, collapse = ", "),
           " | criteria_mode=", criteria_mode,
           " | empty=", empty,
           " | chains=", chains, " cores=", n_cores)
  if (n_cores > 1L) {
    progress("Chains will run in parallel (brms cores=", n_cores, ").")
  } else {
    progress("Chains will run sequentially (cores=1).")
  }
  if (isTRUE(all) && !isTRUE(empty)) {
    progress(
      "NOTE: --all fits ", length(ALL_DATASETS), " datasets sequentially. ",
      "First Stan compile can take several quiet minutes per dataset."
    )
  }
  outs <- character()
  for (ds in datasets) {
    progress(sprintf("==== dataset %s (%d / %d) ====",
                     ds, match(ds, datasets), length(datasets)))
    outs <- c(outs, fit_one_dataset(
      dataset = ds,
      repo_root = repo_root,
      out_root = out_root_abs,
      n_ratings = as.integer(n_ratings),
      n_chains = as.integer(chains),
      n_cores = n_cores,
      n_iter = as.integer(iter),
      n_warmup = as.integer(warmup),
      criteria_mode = criteria_mode,
      seed = as.integer(seed),
      empty_fit = isTRUE(empty),
      max_subjects = if (is.null(max_subjects)) NULL else as.integer(max_subjects),
      backend = backend
    ))
  }
  invisible(outs)
}

setup_backend <- function() {
  backend <- "rstan"
  if (requireNamespace("cmdstanr", quietly = TRUE)) {
    suppressPackageStartupMessages(library(cmdstanr))
    cand <- file.path(Sys.getenv("CONDA_PREFIX", unset = ""), "bin", "cmdstan")
    if (!dir.exists(cand)) {
      cand <- "/root/anaconda3/envs/motivbelief/bin/cmdstan"
    }
    if (dir.exists(cand)) {
      cmdstanr::set_cmdstan_path(cand)
    }
    backend <- tryCatch({
      p <- cmdstanr::cmdstan_path()
      if (is.null(p) || !nzchar(p)) "rstan" else "cmdstanr"
    }, error = function(e) "rstan")
  }
  progress("brms backend: ", backend)
  backend
}

# ---- Data prep -----------------------------------------------------------

conf_bin_edges <- function(conf, n_ratings = 6L) {
  lo <- min(50, min(conf, na.rm = TRUE))
  hi <- max(100, max(conf, na.rm = TRUE))
  seq(lo, hi, length.out = n_ratings + 1L)
}

discretize_confidence <- function(conf, edges) {
  # match Python: digitize(conf, edges[2:-1], right=True) + 1, clip to 1..K
  cuts <- edges[-c(1L, length(edges))]
  bins <- findInterval(conf, cuts, rightmost.closed = TRUE, left.open = FALSE) + 1L
  # findInterval with left.open=FALSE is left-closed; Python digitize(..., right=True)
  # uses right edges. Close enough for equal-width bins; clamp explicitly.
  pmin(pmax(bins, 1L), length(edges) - 1L)
}

load_real_free <- function(experiment, data_dir) {
  path <- file.path(data_dir, sprintf("data_%s.csv", experiment))
  df <- read.csv(path, stringsAsFactors = FALSE)
  df <- df[df$choiceType == "Free" & !is.na(df$conf), , drop = FALSE]
  side <- ifelse(df$dir == "right", 1, -1)
  df$stim <- as.numeric(df$coh) * side
  df$a <- ifelse(df$resp == "right", 1, -1)
  df$correct <- as.integer(df$correct)
  df$experiment <- experiment
  df$participant <- as.character(df$participant)
  df$subject_id <- paste(experiment, df$participant, sep = "_")
  df
}

load_sim_free <- function(dataset, sims_dir) {
  path <- file.path(sims_dir, SIM_FILES[[dataset]])
  df <- read.csv(path, stringsAsFactors = FALSE)
  if ("choiceType" %in% names(df)) {
    df <- df[df$choiceType == "Free", , drop = FALSE]
  }
  df <- df[!is.na(df$conf), , drop = FALSE]
  if (!"coh" %in% names(df)) {
    df$coh <- abs(as.numeric(df$stim))
  }
  df$participant <- as.character(df$participant)
  df$subject_id <- paste(dataset, df$participant, sep = "_")
  df$experiment <- dataset
  df$a <- as.numeric(df$a)
  df$stim <- as.numeric(df$stim)
  df
}

load_merged_free <- function(data_dir) {
  # Pool Free trials from exp1a + exp2 (matches BMC / param-violin "merged").
  dplyr::bind_rows(
    load_real_free("exp1a", data_dir),
    load_real_free("exp2", data_dir)
  )
}

load_dataset <- function(dataset, repo_root) {
  if (dataset %in% REAL_DATASETS) {
    return(load_real_free(dataset, file.path(repo_root, "data")))
  }
  if (dataset %in% MERGED_DATASETS) {
    return(load_merged_free(file.path(repo_root, "data")))
  }
  if (dataset %in% SIM_DATASETS) {
    return(load_sim_free(dataset, file.path(repo_root, "results", "sims")))
  }
  stop("Unknown dataset: ", dataset, call. = FALSE)
}

# Coherence → ordered 3-level numeric: low={1,3}, mid={5}, high={9,38}
COH3_MAP <- c(
  `1` = -1, `3` = -1,
  `5` = 0,
  `9` = 1, `38` = 1
)

coh_to_coh3 <- function(coh) {
  keys <- as.character(as.integer(round(as.numeric(coh))))
  out <- unname(COH3_MAP[keys])
  if (anyNA(out)) {
    bad <- sort(unique(coh[is.na(out)]))
    stop("Unmapped coherence level(s): ", paste(bad, collapse = ", "),
         call. = FALSE)
  }
  as.numeric(out)
}

prepare_trials <- function(raw, dataset, n_ratings = 6L) {
  conf <- as.numeric(raw$conf)
  edges <- conf_bin_edges(conf, n_ratings)
  conf_bin <- discretize_confidence(conf, edges)

  stim01 <- as.integer(as.numeric(raw$stim) > 0)
  resp01 <- as.integer(as.numeric(raw$a) > 0)

  inc_raw <- as.numeric(raw$incentive)
  inc_levels <- sort(unique(inc_raw[is.finite(inc_raw)]))
  # Factor with sorted numeric levels as character labels (e.g. "-1","0","1")
  incentive <- factor(
    as.character(inc_raw),
    levels = as.character(inc_levels)
  )
  inc_meta <- list(
    scheme = "factor",
    levels = as.list(as.character(inc_levels)),
    raw_levels = as.list(inc_levels),
    note = "incentive as unordered factor; treatment contrasts (first level = reference)"
  )

  coh <- as.numeric(raw$coh)
  coh3 <- coh_to_coh3(coh)
  coh3_meta <- list(
    scheme = "ordered3",
    map = as.list(COH3_MAP),
    levels = as.list(c(-1, 0, 1)),
    labels = list(low = list(1L, 3L), mid = list(5L), high = list(9L, 38L)),
    note = "low={1,3}->-1; mid={5}->0; high={9,38}->+1 (linear slope on coh3)"
  )

  out <- data.frame(
    participant = as.character(raw$subject_id),
    stimulus = stim01,
    response = resp01,
    confidence = as.integer(conf_bin),
    incentive = incentive,
    coh3 = as.numeric(coh3),
    coh = coh,
    incentive_raw = inc_raw,
    stringsAsFactors = FALSE
  )
  # Preserve factor after data.frame()
  out$incentive <- incentive

  prep_meta <- list(
    dataset = dataset,
    n_ratings = n_ratings,
    conf_edges = as.list(edges),
    incentive_coding = inc_meta,
    coh3_coding = coh3_meta,
    n_trials = nrow(out),
    n_participants = length(unique(out$participant))
  )
  list(trials = out, prep_meta = prep_meta)
}

# ---- Fit + export --------------------------------------------------------

empty_csv <- function(path, cols) {
  write.csv(
    setNames(data.frame(matrix(ncol = length(cols), nrow = 0)), cols),
    path,
    row.names = FALSE
  )
}

fit_one_dataset <- function(
    dataset,
    repo_root,
    out_root,
    n_ratings = 6L,
    n_chains = 4L,
    n_cores = 4L,
    n_iter = 2000L,
    n_warmup = 1000L,
    criteria_mode = "default",
    seed = 1L,
    empty_fit = FALSE,
    max_subjects = NULL,
    backend = "cmdstanr"
) {
  criteria_mode <- normalize_criteria_mode(criteria_mode)
  if (!criteria_mode %in% c("default", "shared")) {
    stop("criteria_mode must be 'default' or 'shared'")
  }

  out_dir <- file.path(out_root, dataset)
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

  raw <- load_dataset(dataset, repo_root)
  if (!is.null(max_subjects) && max_subjects > 0L) {
    keep <- sort(unique(raw$subject_id))[seq_len(min(max_subjects, length(unique(raw$subject_id))))]
    raw <- raw[raw$subject_id %in% keep, , drop = FALSE]
    progress(sprintf("[%s] subset to %d subjects (smoke test)", dataset, length(keep)))
  }
  progress(sprintf(
    "[%s] loaded %d Free trials, %d subjects",
    dataset, nrow(raw), length(unique(raw$subject_id))
  ))

  prep <- prepare_trials(raw, dataset, n_ratings = n_ratings)
  d <- prep$trials
  prep_meta <- prep$prep_meta
  write.csv(d, file.path(out_dir, "trials_prepared.csv"), row.names = FALSE)
  write_json(prep_meta, file.path(out_dir, "preparation.json"), auto_unbox = TRUE, pretty = TRUE)
  progress(sprintf("[%s] prepared trials -> %s", dataset, out_dir))

  d$participant <- as.factor(as.character(d$participant))
  d$stimulus <- as.integer(d$stimulus)
  d$response <- as.integer(d$response)
  d$confidence <- as.integer(d$confidence)
  d$coh3 <- as.numeric(d$coh3)
  # Restore incentive factor with levels from preparation meta
  inc_lvls <- unlist(prep_meta$incentive_coding$levels)
  d$incentive <- factor(as.character(d$incentive), levels = as.character(inc_lvls))

  K <- as.integer(n_ratings)
  stopifnot(min(d$confidence) >= 1L, max(d$confidence) <= K)

  f <- build_metad_formula(criteria_mode, K)
  progress(sprintf("[%s] formula mode=%s", dataset, criteria_mode))

  agg_for_prior <- aggregate_metad(
    d, participant, incentive, coh3,
    .stimulus = "stimulus", .response = "response", .confidence = "confidence",
    K = K
  )
  priors <- default_prior(f, data = agg_for_prior, family = metad(K = K))
  flat <- is.na(priors$prior) | priors$prior == "" | priors$prior == "(flat)"
  priors$prior[flat & priors$class %in% c("Intercept", "b")] <- "normal(0, 1)"

  progress(sprintf(
    "[%s] fitting hmetad: n_trials=%d n_subj=%d K=%d mode=%s chains=%d cores=%d iter=%d warmup=%d",
    dataset, nrow(d), nlevels(d$participant), K, criteria_mode,
    n_chains, n_cores, n_iter, n_warmup
  ))
  if (!empty_fit) {
    progress(sprintf(
      "[%s] NOTE: first Stan compile for this formula can take several quiet minutes; ",
      dataset
    ), "MCMC iteration lines appear only after compile finishes.")
  }

  fit_args <- list(
    formula = f,
    data = d,
    K = K,
    prior = priors,
    chains = n_chains,
    cores = n_cores,
    iter = n_iter,
    warmup = n_warmup,
    seed = seed,
    init = "0",
    # More frequent iteration prints once sampling starts
    refresh = max(10L, as.integer(n_iter / 50)),
    backend = backend
  )
  if (empty_fit) {
    fit_args$empty <- TRUE
    fit_args$backend <- NULL
    fit_args <- fit_args[!vapply(fit_args, is.null, logical(1))]
    progress("empty=TRUE: building model without MCMC sampling")
  }
  progress(sprintf("[%s] calling fit_metad() ...", dataset))
  fit <- do.call(fit_metad, fit_args)
  progress(sprintf("[%s] fit_metad() finished; writing outputs", dataset))
  saveRDS(fit, file.path(out_dir, "fit.rds"))

  if (empty_fit) {
    empty_csv(
      file.path(out_dir, "group_summary.csv"),
      c("param", "mean", "sd", "q2.5", "q97.5", "rhat", "bulk_ess", "tail_ess", "mratio_at_ref")
    )
    empty_csv(
      file.path(out_dir, "subject_summary.csv"),
      c("participant", "param", "mean", "sd", "q2.5", "q97.5")
    )
    empty_csv(
      file.path(out_dir, "draws_population.csv"),
      c(".chain", ".iteration", ".draw", "variable", "value")
    )
    empty_csv(
      file.path(out_dir, "cell_mratio_summary.csv"),
      c("incentive", "coh3", ".variable", "mean", "sd", "q2.5", "q50", "q97.5")
    )
  } else {
    sm <- summary(fit)
    fixed <- as.data.frame(sm$fixed)
    fixed$param <- rownames(fixed)
    rownames(fixed) <- NULL
    group_rows <- list(fixed[, c(
      "param", "Estimate", "Est.Error", "l-95% CI", "u-95% CI", "Rhat", "Bulk_ESS", "Tail_ESS"
    )])
    if (!is.null(sm$random) && length(sm$random)) {
      for (nm in names(sm$random)) {
        rnd <- as.data.frame(sm$random[[nm]])
        rnd$param <- paste0("sd_or_cor[", nm, "]_", rownames(rnd))
        rownames(rnd) <- NULL
        keep <- intersect(c(
          "param", "Estimate", "Est.Error", "l-95% CI", "u-95% CI", "Rhat", "Bulk_ESS", "Tail_ESS"
        ), names(rnd))
        group_rows[[length(group_rows) + 1L]] <- rnd[, keep, drop = FALSE]
      }
    }
    group_df <- bind_rows(group_rows)
    names(group_df) <- c(
      "param", "mean", "sd", "q2.5", "q97.5", "rhat", "bulk_ess", "tail_ess"
    )[seq_len(ncol(group_df))]
    if ("Intercept" %in% group_df$param) {
      mu0 <- group_df$mean[group_df$param == "Intercept"][1]
      group_df$mratio_at_ref <- ifelse(group_df$param == "Intercept", exp(mu0), NA_real_)
    } else {
      group_df$mratio_at_ref <- NA_real_
    }
    write.csv(group_df, file.path(out_dir, "group_summary.csv"), row.names = FALSE)

    cf <- coef(fit)
    subj_list <- list()
    if (!is.null(cf)) {
      arr <- if (is.list(cf) && !is.null(cf$participant)) cf$participant else cf
      if (length(dim(arr)) == 3L) {
        params <- dimnames(arr)[[3]]
        mu_params <- params[!grepl("^(dprime_|c_|metac2)", params)]
        dprime_params <- params[grepl("^dprime_", params)]
        keep_params <- unique(c(mu_params, dprime_params))
        stat_names <- dimnames(arr)[[2]]
        est <- if ("Estimate" %in% stat_names) "Estimate" else stat_names[[1]]
        err <- if ("Est.Error" %in% stat_names) "Est.Error" else est
        qlo <- if ("Q2.5" %in% stat_names) "Q2.5" else est
        qhi <- if ("Q97.5" %in% stat_names) "Q97.5" else est
        for (pid in dimnames(arr)[[1]]) {
          for (p in keep_params) {
            if (!p %in% params) next
            subj_list[[length(subj_list) + 1L]] <- data.frame(
              participant = pid,
              param = p,
              mean = as.numeric(arr[pid, est, p]),
              sd = as.numeric(arr[pid, err, p]),
              q2.5 = as.numeric(arr[pid, qlo, p]),
              q97.5 = as.numeric(arr[pid, qhi, p]),
              stringsAsFactors = FALSE
            )
          }
        }
      }
    }
    subj_df <- if (length(subj_list)) bind_rows(subj_list) else data.frame(
      participant = character(), param = character(),
      mean = numeric(), sd = numeric(), q2.5 = numeric(), q97.5 = numeric()
    )
    if (nrow(subj_df) && "Intercept" %in% subj_df$param) {
      ref <- subj_df[subj_df$param == "Intercept", ]
      ref$param <- "mratio_at_ref"
      ref$mean <- exp(ref$mean)
      ref$sd <- NA_real_
      ref$q2.5 <- exp(ref$q2.5)
      ref$q97.5 <- exp(ref$q97.5)
      subj_df <- bind_rows(subj_df, ref)
    }
    write.csv(subj_df, file.path(out_dir, "subject_summary.csv"), row.names = FALSE)

    draws <- as_draws_df(fit)
    keep_cols <- names(draws)[
      grepl("^(b_|sd_|cor_)", names(draws)) |
        names(draws) %in% c(".chain", ".iteration", ".draw")
    ]
    pop_long <- pivot_longer(
      draws[, keep_cols, drop = FALSE],
      cols = -c(".chain", ".iteration", ".draw"),
      names_to = "variable",
      values_to = "value"
    )
    write.csv(pop_long, file.path(out_dir, "draws_population.csv"), row.names = FALSE)
    # Rich posterior store (full draws object) alongside CSV summaries
    saveRDS(draws, file.path(out_dir, "draws.rds"))

    newdata <- tidyr::expand_grid(
      incentive = levels(d$incentive),
      coh3 = c(-1, 0, 1)
    )
    newdata$incentive <- factor(newdata$incentive, levels = levels(d$incentive))
    newdata$coh3 <- as.numeric(newdata$coh3)
    # Population predictions (no REs): M-ratio, d', and meta-d' ≈ M × d'
    pl_mu <- tryCatch(
      posterior_linpred(fit, newdata = newdata, re_formula = NA, dpar = "mu"),
      error = function(e) NULL
    )
    pl_dp <- tryCatch(
      posterior_linpred(fit, newdata = newdata, re_formula = NA, dpar = "dprime"),
      error = function(e) NULL
    )
    if (!is.null(pl_mu)) {
      cell_rows <- lapply(seq_len(nrow(newdata)), function(i) {
        m <- exp(pl_mu[, i])
        rows <- list(data.frame(
          incentive = as.character(newdata$incentive[i]),
          coh3 = newdata$coh3[i],
          .variable = "M",
          mean = mean(m), sd = sd(m),
          q2.5 = as.numeric(quantile(m, 0.025)),
          q50 = as.numeric(quantile(m, 0.5)),
          q97.5 = as.numeric(quantile(m, 0.975)),
          stringsAsFactors = FALSE
        ))
        if (!is.null(pl_dp)) {
          dp <- pl_dp[, i]
          md <- m * dp
          rows[[length(rows) + 1L]] <- data.frame(
            incentive = as.character(newdata$incentive[i]),
            coh3 = newdata$coh3[i],
            .variable = "dprime",
            mean = mean(dp), sd = sd(dp),
            q2.5 = as.numeric(quantile(dp, 0.025)),
            q50 = as.numeric(quantile(dp, 0.5)),
            q97.5 = as.numeric(quantile(dp, 0.975)),
            stringsAsFactors = FALSE
          )
          rows[[length(rows) + 1L]] <- data.frame(
            incentive = as.character(newdata$incentive[i]),
            coh3 = newdata$coh3[i],
            .variable = "meta_d",
            mean = mean(md), sd = sd(md),
            q2.5 = as.numeric(quantile(md, 0.025)),
            q50 = as.numeric(quantile(md, 0.5)),
            q97.5 = as.numeric(quantile(md, 0.975)),
            stringsAsFactors = FALSE
          )
        }
        bind_rows(rows)
      })
      write.csv(bind_rows(cell_rows), file.path(out_dir, "cell_mratio_summary.csv"), row.names = FALSE)
    } else {
      empty_csv(
        file.path(out_dir, "cell_mratio_summary.csv"),
        c("incentive", "coh3", ".variable", "mean", "sd", "q2.5", "q50", "q97.5")
      )
    }
  }

  meta <- list(
    package = "hmetad",
    hmetad_version = as.character(packageVersion("hmetad")),
    brms_version = as.character(packageVersion("brms")),
    backend = if (empty_fit) "empty" else backend,
    criteria_mode = criteria_mode,
    K = K,
    n_chains = n_chains,
    n_cores = n_cores,
    n_iter = n_iter,
    n_warmup = n_warmup,
    seed = seed,
    empty = empty_fit,
    n_trials = nrow(d),
    n_participants = nlevels(d$participant),
    formula = paste(deparse(f), collapse = " "),
    preparation = prep_meta,
    outputs = list(
      fit_rds = "fit.rds",
      draws_rds = "draws.rds",
      draws_population = "draws_population.csv",
      group_summary = "group_summary.csv",
      subject_summary = "subject_summary.csv",
      cell_mratio_summary = "cell_mratio_summary.csv"
    )
  )
  write_json(meta, file.path(out_dir, "meta.json"), auto_unbox = TRUE, pretty = TRUE)

  progress(sprintf("[%s] done -> %s", dataset, out_dir))
  if (!empty_fit && exists("group_df") && nrow(group_df)) {
    progress(sprintf("max Rhat (fixed): %.4f", max(group_df$rhat, na.rm = TRUE)))
  }
  invisible(out_dir)
}

# ---- main (Rscript only; never quit() in interactive / RStudio) ------------

.is_rscript <- function() {
  # TRUE when launched as Rscript path/to/fit_hmeta_d.R ...
  args <- commandArgs(FALSE)
  any(startsWith(args, "--file=")) && !interactive()
}

if (.is_rscript()) {
  opts <- parse_args(commandArgs(trailingOnly = TRUE))
  if (opts$help || (!opts$all && is.null(opts$dataset))) {
    print_help()
    quit(status = if (opts$help) 0L else 1L)
  }
  run_fit_hmeta_d(
    dataset = opts$dataset,
    all = opts$all,
    out_root = opts$out_root,
    repo_root = opts$repo_root,
    n_ratings = opts$n_ratings,
    chains = opts$chains,
    cores = opts$cores,
    iter = opts$iter,
    warmup = opts$warmup,
    criteria_mode = opts$criteria_mode,
    seed = opts$seed,
    empty = opts$empty,
    max_subjects = opts$max_subjects
  )
} else if (interactive() && !length(commandArgs(trailingOnly = TRUE))) {
  message(
    "Loaded fit_hmeta_d.R. In RStudio call e.g.\n",
    "  run_fit_hmeta_d(dataset = \"exp1a\", empty = TRUE, max_subjects = 3L)\n",
    "Or from a terminal:\n",
    "  Rscript scripts/r/fit_hmeta_d.R --dataset exp1a"
  )
}
