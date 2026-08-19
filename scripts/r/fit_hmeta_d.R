#!/usr/bin/env Rscript
#
# Primary meta-d′ analysis: per-participant Bayesian fits via CRAN hmetad (brms).
#
# Fits each participant × choiceType (Free / Observed / Forced / Replayed as present).
# Legacy alternatives:
#   hierarchical → scripts/r/_old/fit_hmeta_d_hierarchical.R
#   MLE cells    → python scripts/_old/fit_hmeta_d_mle.py
#
# Usage:
#   Rscript scripts/r/fit_hmeta_d.R --dataset exp1a
#   Rscript scripts/r/fit_hmeta_d.R --all
#   Rscript scripts/r/fit_hmeta_d.R --dataset exp1a --max-subjects 2
#   Rscript scripts/r/fit_hmeta_d.R --dataset exp3 --choice-types Forced Replayed
#   python scripts/fit_hmeta_d.py --dataset exp1a   # thin wrapper → this script
#
# Datasets:
#   exp1a, exp1b, exp2, exp3, sim_act, sim_intent, sim_confirm
#   (no separate merged fit; plotter pools exp1a+exp2 for data-vs-models)
#
# Outputs under results/hmeta_d/<dataset>/:
#   preparation.json, trials_prepared.csv, meta.json,
#   subject_summary.csv, group_summary.csv, cell_mratio_summary.csv,
#   subject_effects.csv, convergence_qc.csv,
#   subjects/<id>__<choiceType>.rds (optional, --save-fits)

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

REAL_DATASETS <- c("exp1a", "exp1b", "exp2", "exp3")
SIM_DATASETS <- c("sim_act", "sim_intent", "sim_confirm")
ALL_DATASETS <- c(REAL_DATASETS, SIM_DATASETS)
SIM_FILES <- c(
  sim_act = "sims_act.csv",
  sim_intent = "sims_intent.csv",
  sim_confirm = "sims_confirm.csv"
)
DEFAULT_CHOICE_TYPES <- c("Free", "Observed", "Forced", "Replayed")

parse_args <- function(argv) {
  opts <- list(
    dataset = NULL,
    all = FALSE,
    out_root = "results/hmeta_d",
    repo_root = NULL,
    n_ratings = 6L,
    chains = 4L,
    cores = NULL,
    iter = 5000L,
    warmup = 1000L,
    criteria_mode = "default",
    seed = 1L,
    empty = FALSE,
    max_subjects = NULL,
    save_fits = FALSE,
    choice_types = NULL,
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
    } else if (a == "--save-fits") {
      opts$save_fits <- TRUE
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
    } else if (a == "--choice-types") {
      cts <- character()
      while (i + 1L <= length(argv) && !startsWith(argv[[i + 1L]], "-")) {
        i <- i + 1L
        cts <- c(cts, strsplit(argv[[i]], ",", fixed = TRUE)[[1]])
      }
      opts$choice_types <- trimws(cts[nzchar(trimws(cts))])
    } else {
      stop("Unknown argument: ", a, call. = FALSE)
    }
    i <- i + 1L
  }
  opts
}

print_help <- function() {
  cat(paste(
    "Fit per-participant Bayesian meta-d' (incentive × coh3) with CRAN hmetad.",
    "One fit per participant × choiceType (Free/Observed/Forced/Replayed).",
    "Legacy hierarchical: scripts/r/_old/fit_hmeta_d_hierarchical.R",
    "Legacy MLE: python scripts/_old/fit_hmeta_d_mle.py",
    "",
    "Usage:",
    "  Rscript scripts/r/fit_hmeta_d.R --dataset exp1a",
    "  Rscript scripts/r/fit_hmeta_d.R --dataset exp3 --choice-types Forced Replayed",
    "  Rscript scripts/r/fit_hmeta_d.R --all",
    "  python scripts/fit_hmeta_d.py --dataset exp1a",
    "",
    "Options:",
    "  --dataset NAME       One of: exp1a, exp1b, exp2, exp3, sim_act, sim_intent, sim_confirm",
    "  --all                Fit all datasets",
    "  --choice-types ...   Subset of Free Observed Forced Replayed (default: all four;",
    "                       only levels present in the data are used)",
    "  --out-root DIR       Output root (default: results/hmeta_d)",
    "  --repo-root DIR      Repository root (default: auto from script path)",
    "  --n-ratings K        Equal-width conf bins on [0,100] (default: 6)",
    "  --chains N           MCMC chains per subject (default: 2)",
    "  --cores N            Parallel cores for chains (default: min(chains, detectCores()))",
    "  --iter N             Total iterations per chain (default: 2000)",
    "  --warmup N           Warmup iterations (default: 1000)",
    "  --criteria-mode M    default | shared (default: default)",
    "                       default: logM~inc*coh3; d'~coh3; c~1; type2~inc",
    "                       shared:  same but type2 criteria ~1 only",
    "  --seed N             RNG seed (default: 1)",
    "  --max-subjects N     Cap unique participants (smoke tests)",
    "  --save-fits          Write subjects/<id>__<choiceType>.rds (large)",
    "  --empty              Build model without MCMC (first unit only)",
    "  -h, --help           Show this help",
    sep = "\n"
  ), "\n")
}

normalize_choice_types <- function(choice_types) {
  if (is.null(choice_types) || !length(choice_types)) {
    return(DEFAULT_CHOICE_TYPES)
  }
  out <- unique(as.character(choice_types))
  out <- out[nzchar(out)]
  bad <- setdiff(out, DEFAULT_CHOICE_TYPES)
  if (length(bad)) {
    stop(
      "Unknown choiceType(s): ", paste(bad, collapse = ", "),
      " (allowed: ", paste(DEFAULT_CHOICE_TYPES, collapse = ", "), ")",
      call. = FALSE
    )
  }
  out
}

normalize_criteria_mode <- function(mode) {
  if (identical(mode, "full")) {
    progress("NOTE: --criteria-mode full is deprecated; using 'default' structure.")
    return("default")
  }
  mode
}

#' Individual-subject formulas (no random effects).
#'
#' default:
#'   mu ~ incentive * coh3
#'   dprime ~ coh3
#'   c ~ 1
#'   type-2 ~ incentive
#' shared: type-2 ~ 1
build_metad_formula <- function(criteria_mode, K) {
  mc <- metac2_parameters(K = K)
  t2 <- paste(mc, collapse = " + ")

  if (criteria_mode == "default") {
    f <- bf(
      N ~ incentive * coh3,
      dprime ~ coh3,
      c ~ 1,
      as.formula(paste(t2, "~ incentive"))
    )
  } else if (criteria_mode == "shared") {
    f <- bf(
      N ~ incentive * coh3,
      dprime ~ coh3,
      c ~ 1,
      as.formula(paste(t2, "~ 1"))
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
  # Rscript: scripts/r/fit_hmeta_d.R -> repo root is two levels up
  script <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE))
  if (length(script) && nzchar(script[[1]])) {
    cand <- normalizePath(file.path(dirname(script[[1]]), "..", ".."), mustWork = FALSE)
    if (dir.exists(file.path(cand, "data")) && dir.exists(file.path(cand, "scripts"))) {
      return(cand)
    }
  }
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

resolve_cores <- function(cores, chains) {
  n_chains <- as.integer(chains)
  if (is.null(cores) || is.na(cores)) {
    n_avail <- parallel::detectCores()
    if (is.na(n_avail) || n_avail < 1L) n_avail <- 1L
    cores <- min(n_chains, n_avail)
  }
  as.integer(max(1L, cores))
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

conf_bin_edges <- function(n_ratings = 6L, lo = 0, hi = 100) {
  if (as.integer(n_ratings) < 2L) stop("n_ratings must be >= 2", call. = FALSE)
  seq(as.numeric(lo), as.numeric(hi), length.out = as.integer(n_ratings) + 1L)
}

discretize_confidence <- function(conf, edges) {
  cuts <- edges[-c(1L, length(edges))]
  bins <- findInterval(conf, cuts, rightmost.closed = TRUE, left.open = FALSE) + 1L
  pmin(pmax(bins, 1L), length(edges) - 1L)
}

load_real <- function(experiment, data_dir, choice_types = DEFAULT_CHOICE_TYPES) {
  path <- file.path(data_dir, sprintf("data_%s.csv", experiment))
  df <- read.csv(path, stringsAsFactors = FALSE)
  keep <- normalize_choice_types(choice_types)
  df <- df[df$choiceType %in% keep & !is.na(df$conf), , drop = FALSE]
  if (!nrow(df)) {
    stop(
      "No trials for ", experiment, " with choiceType in {",
      paste(keep, collapse = ", "), "}",
      call. = FALSE
    )
  }
  side <- ifelse(df$dir == "right", 1, -1)
  df$stim <- as.numeric(df$coh) * side
  df$a <- ifelse(df$resp == "right", 1, -1)
  df$correct <- as.integer(df$correct)
  df$experiment <- experiment
  df$participant <- as.character(df$participant)
  df$choiceType <- as.character(df$choiceType)
  df$subject_id <- paste(experiment, df$participant, sep = "_")
  df
}

load_sim <- function(dataset, sims_dir, choice_types = DEFAULT_CHOICE_TYPES) {
  path <- file.path(sims_dir, SIM_FILES[[dataset]])
  df <- read.csv(path, stringsAsFactors = FALSE)
  keep <- normalize_choice_types(choice_types)
  if ("choiceType" %in% names(df)) {
    df$choiceType <- as.character(df$choiceType)
    df <- df[df$choiceType %in% keep, , drop = FALSE]
  } else {
    df$choiceType <- "Free"
  }
  df <- df[!is.na(df$conf), , drop = FALSE]
  if (!nrow(df)) {
    stop(
      "No trials for ", dataset, " with choiceType in {",
      paste(keep, collapse = ", "), "}",
      call. = FALSE
    )
  }
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

load_dataset <- function(dataset, repo_root, choice_types = DEFAULT_CHOICE_TYPES) {
  if (dataset %in% REAL_DATASETS) {
    return(load_real(dataset, file.path(repo_root, "data"), choice_types = choice_types))
  }
  if (dataset %in% SIM_DATASETS) {
    return(load_sim(
      dataset, file.path(repo_root, "results", "sims"),
      choice_types = choice_types
    ))
  }
  stop("Unknown dataset: ", dataset, call. = FALSE)
}

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
  edges <- conf_bin_edges(n_ratings)
  conf_bin <- discretize_confidence(conf, edges)

  stim01 <- as.integer(as.numeric(raw$stim) > 0)
  resp01 <- as.integer(as.numeric(raw$a) > 0)

  inc_raw <- as.numeric(raw$incentive)
  inc_levels <- sort(unique(inc_raw[is.finite(inc_raw)]))
  incentive <- factor(as.character(inc_raw), levels = as.character(inc_levels))
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
    choiceType = as.character(raw$choiceType),
    stimulus = stim01,
    response = resp01,
    confidence = as.integer(conf_bin),
    incentive = incentive,
    coh3 = as.numeric(coh3),
    coh = coh,
    stringsAsFactors = FALSE
  )

  ctype_levels <- DEFAULT_CHOICE_TYPES[DEFAULT_CHOICE_TYPES %in% unique(out$choiceType)]
  ctype_levels <- c(ctype_levels, setdiff(sort(unique(out$choiceType)), ctype_levels))

  prep_meta <- list(
    dataset = dataset,
    fit_mode = "bayes_individual",
    n_ratings = as.integer(n_ratings),
    conf_edges = as.list(as.numeric(edges)),
    conf_binning = list(scheme = "equal_width", lo = 0, hi = 100),
    choice_types = as.list(ctype_levels),
    incentive_coding = inc_meta,
    coh3_coding = coh3_meta,
    n_trials = nrow(out),
    n_participants = length(unique(out$participant)),
    n_fit_units = nrow(unique(out[, c("participant", "choiceType"), drop = FALSE]))
  )
  list(trials = out, prep_meta = prep_meta)
}

# ---- Fit helpers ---------------------------------------------------------

empty_csv <- function(path, cols) {
  write.csv(
    setNames(data.frame(matrix(ncol = length(cols), nrow = 0)), cols),
    path,
    row.names = FALSE
  )
}

summarize_fixed <- function(fit) {
  sm <- summary(fit)
  fixed <- as.data.frame(sm$fixed)
  fixed$param <- rownames(fixed)
  rownames(fixed) <- NULL
  keep <- c("param", "Estimate", "Est.Error", "l-95% CI", "u-95% CI", "Rhat", "Bulk_ESS", "Tail_ESS")
  keep <- intersect(keep, names(fixed))
  out <- fixed[, keep, drop = FALSE]
  names(out) <- c(
    "param", "mean", "sd", "q2.5", "q97.5", "rhat", "bulk_ess", "tail_ess"
  )[seq_len(ncol(out))]
  out
}

cell_preds_from_fit <- function(fit, incentive_levels) {
  newdata <- tidyr::expand_grid(
    incentive = as.character(incentive_levels),
    coh3 = c(-1, 0, 1)
  )
  newdata$incentive <- factor(newdata$incentive, levels = as.character(incentive_levels))
  newdata$coh3 <- as.numeric(newdata$coh3)
  pl_mu <- tryCatch(
    posterior_linpred(fit, newdata = newdata, re_formula = NA, dpar = "mu"),
    error = function(e) NULL
  )
  pl_dp <- tryCatch(
    posterior_linpred(fit, newdata = newdata, re_formula = NA, dpar = "dprime"),
    error = function(e) NULL
  )
  if (is.null(pl_mu)) return(NULL)
  rows <- lapply(seq_len(nrow(newdata)), function(i) {
    m <- exp(pl_mu[, i])
    out <- list(data.frame(
      incentive = as.character(newdata$incentive[i]),
      coh3 = newdata$coh3[i],
      .variable = "M",
      mean = mean(m),
      q50 = as.numeric(quantile(m, 0.5)),
      stringsAsFactors = FALSE
    ))
    if (!is.null(pl_dp)) {
      dp <- pl_dp[, i]
      md <- m * dp
      out[[length(out) + 1L]] <- data.frame(
        incentive = as.character(newdata$incentive[i]),
        coh3 = newdata$coh3[i],
        .variable = "dprime",
        mean = mean(dp),
        q50 = as.numeric(quantile(dp, 0.5)),
        stringsAsFactors = FALSE
      )
      out[[length(out) + 1L]] <- data.frame(
        incentive = as.character(newdata$incentive[i]),
        coh3 = newdata$coh3[i],
        .variable = "meta_d",
        mean = mean(md),
        q50 = as.numeric(quantile(md, 0.5)),
        stringsAsFactors = FALSE
      )
    }
    bind_rows(out)
  })
  bind_rows(rows)
}

effect_row_from_fixed <- function(fixed_df, participant, choice_type) {
  # Mean of non-reference incentive main effects / interactions / type2 incentive.
  params <- fixed_df$param
  mu_inc <- grepl("^incentive[^:]*$", params) & !grepl(":", params)
  mu_ix <- grepl("^incentive.+:coh3$", params)
  t2 <- grepl("^metac2.+_incentive", params)
  data.frame(
    participant = participant,
    choiceType = choice_type,
    mu_incentive = if (any(mu_inc)) mean(fixed_df$mean[mu_inc]) else NA_real_,
    mu_incentive_coh3 = if (any(mu_ix)) mean(fixed_df$mean[mu_ix]) else NA_real_,
    type2_incentive = if (any(t2)) mean(fixed_df$mean[t2]) else NA_real_,
    coh3 = if ("coh3" %in% params) fixed_df$mean[params == "coh3"][1] else NA_real_,
    dprime_coh3 = if ("dprime_coh3" %in% params) {
      fixed_df$mean[params == "dprime_coh3"][1]
    } else {
      NA_real_
    },
    Intercept = if ("Intercept" %in% params) fixed_df$mean[params == "Intercept"][1] else NA_real_,
    dprime_Intercept = if ("dprime_Intercept" %in% params) {
      fixed_df$mean[params == "dprime_Intercept"][1]
    } else {
      NA_real_
    },
    max_rhat = if ("rhat" %in% names(fixed_df)) max(fixed_df$rhat, na.rm = TRUE) else NA_real_,
    stringsAsFactors = FALSE
  )
}

group_summary_from_subjects <- function(subj_df) {
  # Across-subject mean of each param's posterior mean + SEM + one-sample t vs 0,
  # within choiceType.
  if (!"choiceType" %in% names(subj_df)) {
    subj_df$choiceType <- "Free"
  }
  keys <- interaction(subj_df$choiceType, subj_df$param, drop = TRUE, sep = "\r")
  rows <- lapply(split(subj_df, keys), function(g) {
    x <- g$mean[is.finite(g$mean)]
    n <- length(x)
    m <- if (n) mean(x) else NA_real_
    s <- if (n > 1L) sd(x) else NA_real_
    sem <- if (n > 1L) s / sqrt(n) else NA_real_
    tt <- if (n > 1L) tryCatch(stats::t.test(x, mu = 0), error = function(e) NULL) else NULL
    data.frame(
      choiceType = as.character(g$choiceType[1]),
      param = as.character(g$param[1]),
      mean = m,
      sd = s,
      sem = sem,
      n = n,
      q2.5 = if (n) as.numeric(quantile(x, 0.025)) else NA_real_,
      q50 = if (n) as.numeric(quantile(x, 0.5)) else NA_real_,
      q97.5 = if (n) as.numeric(quantile(x, 0.975)) else NA_real_,
      t = if (!is.null(tt)) unname(tt$statistic) else NA_real_,
      df = if (!is.null(tt)) unname(tt$parameter) else NA_real_,
      p = if (!is.null(tt)) tt$p.value else NA_real_,
      stringsAsFactors = FALSE
    )
  })
  bind_rows(rows)
}

aggregate_cell_across_subjects <- function(cell_list) {
  if (!length(cell_list)) return(NULL)
  allc <- bind_rows(cell_list)
  if (!"choiceType" %in% names(allc)) {
    allc$choiceType <- "Free"
  }
  # Prefer posterior mean per subject cell
  allc$est <- ifelse(is.finite(allc$mean), allc$mean, allc$q50)
  rows <- lapply(
    split(allc, list(allc$choiceType, allc$incentive, allc$coh3, allc$.variable), drop = TRUE),
    function(g) {
      x <- g$est[is.finite(g$est)]
      n <- length(x)
      m <- if (n) mean(x) else NA_real_
      s <- if (n > 1L) sd(x) else NA_real_
      sem <- if (n > 1L) s / sqrt(n) else NA_real_
      data.frame(
        choiceType = as.character(g$choiceType[1]),
        incentive = as.character(g$incentive[1]),
        coh3 = as.numeric(g$coh3[1]),
        .variable = as.character(g$.variable[1]),
        mean = m,
        sd = s,
        sem = sem,
        n = n,
        q2.5 = if (n > 1L) m - 1.96 * sem else m,
        q50 = m,
        q97.5 = if (n > 1L) m + 1.96 * sem else m,
        stringsAsFactors = FALSE
      )
    }
  )
  bind_rows(rows)
}

# ---- Main fit ------------------------------------------------------------

#' Run one or more per-participant hmetad fits (safe to call from RStudio).
run_fit_hmeta_d <- function(
    dataset = NULL,
    all = FALSE,
    out_root = "results/hmeta_d",
    repo_root = NULL,
    n_ratings = 6L,
    chains = 2L,
    cores = NULL,
    iter = 5000L,
    warmup = 1000L,
    criteria_mode = "default",
    seed = 1L,
    empty = FALSE,
    max_subjects = NULL,
    save_fits = FALSE,
    choice_types = NULL
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
  choice_types <- normalize_choice_types(choice_types)

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
  progress(
    "mode=bayes_individual | datasets: ", paste(datasets, collapse = ", "),
    " | choiceTypes=", paste(choice_types, collapse = ","),
    " | criteria_mode=", criteria_mode,
    " | empty=", empty,
    " | chains=", chains, " cores=", n_cores
  )

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
      backend = backend,
      save_fits = isTRUE(save_fits),
      choice_types = choice_types
    ))
  }
  invisible(outs)
}

fit_one_dataset <- function(
    dataset,
    repo_root,
    out_root,
    n_ratings = 6L,
    n_chains = 2L,
    n_cores = 2L,
    n_iter = 5000L,
    n_warmup = 1000L,
    criteria_mode = "default",
    seed = 1L,
    empty_fit = FALSE,
    max_subjects = NULL,
    backend = "cmdstanr",
    save_fits = FALSE,
    choice_types = DEFAULT_CHOICE_TYPES
) {
  criteria_mode <- normalize_criteria_mode(criteria_mode)
  choice_types <- normalize_choice_types(choice_types)
  out_dir <- file.path(out_root, dataset)
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
  subj_dir <- file.path(out_dir, "subjects")
  if (save_fits) dir.create(subj_dir, recursive = TRUE, showWarnings = FALSE)

  raw <- load_dataset(dataset, repo_root, choice_types = choice_types)
  if (!is.null(max_subjects) && max_subjects > 0L) {
    keep <- sort(unique(raw$subject_id))[
      seq_len(min(max_subjects, length(unique(raw$subject_id))))
    ]
    raw <- raw[raw$subject_id %in% keep, , drop = FALSE]
    progress(sprintf("[%s] subset to %d subjects (smoke test)", dataset, length(keep)))
  }
  progress(sprintf(
    "[%s] loaded %d trials, %d subjects, choiceTypes={%s}",
    dataset, nrow(raw), length(unique(raw$subject_id)),
    paste(sort(unique(raw$choiceType)), collapse = ", ")
  ))

  prep <- prepare_trials(raw, dataset, n_ratings = n_ratings)
  d <- prep$trials
  prep_meta <- prep$prep_meta
  write.csv(d, file.path(out_dir, "trials_prepared.csv"), row.names = FALSE)
  write_json(prep_meta, file.path(out_dir, "preparation.json"), auto_unbox = TRUE, pretty = TRUE)

  inc_lvls <- as.character(unlist(prep_meta$incentive_coding$levels))
  d$incentive <- factor(as.character(d$incentive), levels = inc_lvls)
  d$coh3 <- as.numeric(d$coh3)
  d$stimulus <- as.integer(d$stimulus)
  d$response <- as.integer(d$response)
  d$confidence <- as.integer(d$confidence)
  d$choiceType <- as.character(d$choiceType)

  K <- as.integer(n_ratings)
  stopifnot(min(d$confidence) >= 1L, max(d$confidence) <= K)
  f <- build_metad_formula(criteria_mode, K)
  progress(sprintf("[%s] formula mode=%s", dataset, criteria_mode))

  # Fit units: participant × choiceType (sims have both Free & Observed within pid)
  units <- unique(d[, c("participant", "choiceType"), drop = FALSE])
  units <- units[order(units$participant, units$choiceType), , drop = FALSE]
  rownames(units) <- NULL

  # Priors from a single-unit aggregate (same formula for all)
  pid0 <- as.character(units$participant[1])
  ctype0 <- as.character(units$choiceType[1])
  d0 <- d[d$participant == pid0 & d$choiceType == ctype0, , drop = FALSE]
  agg0 <- aggregate_metad(
    d0, incentive, coh3,
    .stimulus = "stimulus", .response = "response", .confidence = "confidence",
    K = K
  )
  priors <- default_prior(f, data = agg0, family = metad(K = K))
  flat <- is.na(priors$prior) | priors$prior == "" | priors$prior == "(flat)"
  priors$prior[flat & priors$class %in% c("Intercept", "b")] <- "normal(0, 1)"

  progress(sprintf(
    "[%s] fitting %d units (%d participants) | chains=%d cores=%d iter=%d warmup=%d",
    dataset, nrow(units), length(unique(units$participant)),
    n_chains, n_cores, n_iter, n_warmup
  ))

  unit_label <- function(pid, ctype) paste0(pid, " / ", ctype)
  safe_fname <- function(pid, ctype) {
    paste0(
      gsub("[^A-Za-z0-9_.-]", "_", pid), "__",
      gsub("[^A-Za-z0-9_.-]", "_", ctype), ".rds"
    )
  }

  if (empty_fit) {
    progress("empty=TRUE: building model without MCMC (first unit only)")
    fit_args <- list(
      formula = f, data = d0, K = K, prior = priors,
      empty = TRUE, init = "0"
    )
    fit <- do.call(fit_metad, fit_args)
    if (save_fits) saveRDS(fit, file.path(subj_dir, safe_fname(pid0, ctype0)))
    empty_csv(file.path(out_dir, "subject_summary.csv"),
              c("participant", "choiceType", "param", "mean", "sd", "q2.5", "q97.5",
                "rhat", "bulk_ess", "tail_ess"))
    empty_csv(file.path(out_dir, "group_summary.csv"),
              c("choiceType", "param", "mean", "sd", "sem", "n", "q2.5", "q50", "q97.5",
                "t", "df", "p"))
    empty_csv(file.path(out_dir, "subject_effects.csv"),
              c("participant", "choiceType", "mu_incentive", "mu_incentive_coh3",
                "type2_incentive", "coh3", "dprime_coh3", "Intercept",
                "dprime_Intercept", "max_rhat"))
    empty_csv(file.path(out_dir, "cell_mratio_summary.csv"),
              c("choiceType", "incentive", "coh3", ".variable", "mean", "sd", "sem", "n",
                "q2.5", "q50", "q97.5"))
    empty_csv(file.path(out_dir, "convergence_qc.csv"),
              c("participant", "choiceType", "max_rhat", "min_bulk_ess", "min_tail_ess",
                "qc_pass", "mu_incentive", "mu_incentive_coh3", "type2_incentive",
                "coh3", "dprime_coh3", "Intercept"))
    meta <- list(
      package = "hmetad", fit_mode = "bayes_individual", empty = TRUE,
      criteria_mode = criteria_mode, K = K,
      choice_types = as.list(prep_meta$choice_types),
      n_participants = length(unique(units$participant)),
      n_fit_units = nrow(units),
      formula = paste(deparse(f), collapse = " "), preparation = prep_meta
    )
    write_json(meta, file.path(out_dir, "meta.json"), auto_unbox = TRUE, pretty = TRUE)
    progress(sprintf("[%s] done (empty) -> %s", dataset, out_dir))
    return(out_dir)
  }

  subj_rows <- list()
  effect_rows <- list()
  cell_rows <- list()
  fail <- character()

  for (ii in seq_len(nrow(units))) {
    pid <- as.character(units$participant[ii])
    ctype <- as.character(units$choiceType[ii])
    ulab <- unit_label(pid, ctype)
    progress(sprintf("[%s] unit %d / %d: %s", dataset, ii, nrow(units), ulab))
    di <- d[d$participant == pid & d$choiceType == ctype, , drop = FALSE]
    di$incentive <- factor(as.character(di$incentive), levels = inc_lvls)
    # Need all incentive levels present for contrasts; skip if a level is missing
    if (length(unique(as.character(di$incentive))) < length(inc_lvls)) {
      progress(sprintf("[%s] SKIP %s: missing incentive level(s)", dataset, ulab))
      fail <- c(fail, ulab)
      next
    }
    if (length(unique(di$coh3)) < 2L) {
      progress(sprintf("[%s] SKIP %s: fewer than 2 coh3 levels", dataset, ulab))
      fail <- c(fail, ulab)
      next
    }

    fit_args <- list(
      formula = f,
      data = di,
      K = K,
      prior = priors,
      chains = n_chains,
      cores = n_cores,
      iter = n_iter,
      warmup = n_warmup,
      seed = as.integer(seed + ii),
      init = "0",
      refresh = 0L,
      backend = backend
    )
    fit <- tryCatch(do.call(fit_metad, fit_args), error = function(e) {
      progress(sprintf("[%s] FAIL %s: %s", dataset, ulab, conditionMessage(e)))
      NULL
    })
    if (is.null(fit)) {
      fail <- c(fail, ulab)
      next
    }
    if (save_fits) {
      saveRDS(fit, file.path(subj_dir, safe_fname(pid, ctype)))
    }

    fixed <- summarize_fixed(fit)
    fixed$participant <- pid
    fixed$choiceType <- ctype
    subj_rows[[length(subj_rows) + 1L]] <- fixed[
      , c("participant", "choiceType", "param", "mean", "sd", "q2.5", "q97.5",
          intersect(c("rhat", "bulk_ess", "tail_ess"), names(fixed))),
      drop = FALSE
    ]
    effect_rows[[length(effect_rows) + 1L]] <- effect_row_from_fixed(fixed, pid, ctype)

    cp <- cell_preds_from_fit(fit, inc_lvls)
    if (!is.null(cp)) {
      cp$participant <- pid
      cp$choiceType <- ctype
      cell_rows[[length(cell_rows) + 1L]] <- cp
    }
  }

  subj_df <- if (length(subj_rows)) bind_rows(subj_rows) else data.frame()
  if (nrow(subj_df)) {
    write.csv(subj_df, file.path(out_dir, "subject_summary.csv"), row.names = FALSE)
    write.csv(group_summary_from_subjects(subj_df),
              file.path(out_dir, "group_summary.csv"), row.names = FALSE)
  } else {
    empty_csv(file.path(out_dir, "subject_summary.csv"),
              c("participant", "choiceType", "param", "mean", "sd", "q2.5", "q97.5",
                "rhat", "bulk_ess", "tail_ess"))
    empty_csv(file.path(out_dir, "group_summary.csv"),
              c("choiceType", "param", "mean", "sd", "sem", "n", "q2.5", "q50", "q97.5",
                "t", "df", "p"))
  }

  eff_df <- if (length(effect_rows)) bind_rows(effect_rows) else data.frame()
  if (nrow(eff_df)) {
    write.csv(eff_df, file.path(out_dir, "subject_effects.csv"), row.names = FALSE)
  } else {
    empty_csv(file.path(out_dir, "subject_effects.csv"),
              c("participant", "choiceType", "mu_incentive", "mu_incentive_coh3",
                "type2_incentive", "coh3", "dprime_coh3", "Intercept",
                "dprime_Intercept", "max_rhat"))
  }

  # Convergence QC (R̂ / ESS); used for sensitivity checks, not auto-exclusion
  if (nrow(subj_df) && nrow(eff_df)) {
    if (all(c("bulk_ess", "tail_ess") %in% names(subj_df))) {
      ess <- subj_df %>%
        group_by(participant, choiceType) %>%
        summarise(
          min_bulk_ess = min(bulk_ess, na.rm = TRUE),
          min_tail_ess = min(tail_ess, na.rm = TRUE),
          .groups = "drop"
        )
    } else {
      ess <- data.frame(
        participant = as.character(eff_df$participant),
        choiceType = as.character(eff_df$choiceType),
        min_bulk_ess = NA_real_,
        min_tail_ess = NA_real_,
        stringsAsFactors = FALSE
      )
    }
    qc <- eff_df %>%
      select(participant, choiceType, max_rhat, mu_incentive, mu_incentive_coh3,
             type2_incentive, coh3, dprime_coh3, Intercept) %>%
      left_join(ess, by = c("participant", "choiceType")) %>%
      mutate(
        qc_pass = is.finite(max_rhat) & max_rhat <= 1.01 &
          (is.na(min_bulk_ess) | !is.finite(min_bulk_ess) | min_bulk_ess >= 100)
      )
    write.csv(qc, file.path(out_dir, "convergence_qc.csv"), row.names = FALSE)
    progress(sprintf(
      "[%s] convergence QC: %d / %d pass (max_rhat<=1.01 & min_bulk_ess>=100)",
      dataset, sum(qc$qc_pass, na.rm = TRUE), nrow(qc)
    ))
  } else {
    empty_csv(file.path(out_dir, "convergence_qc.csv"),
              c("participant", "choiceType", "max_rhat", "min_bulk_ess", "min_tail_ess",
                "qc_pass", "mu_incentive", "mu_incentive_coh3", "type2_incentive",
                "coh3", "dprime_coh3", "Intercept"))
  }

  cell_agg <- aggregate_cell_across_subjects(cell_rows)
  if (!is.null(cell_agg) && nrow(cell_agg)) {
    write.csv(cell_agg, file.path(out_dir, "cell_mratio_summary.csv"), row.names = FALSE)
  } else {
    empty_csv(file.path(out_dir, "cell_mratio_summary.csv"),
              c("choiceType", "incentive", "coh3", ".variable", "mean", "sd", "sem", "n",
                "q2.5", "q50", "q97.5"))
  }

  meta <- list(
    package = "hmetad",
    hmetad_version = as.character(packageVersion("hmetad")),
    brms_version = as.character(packageVersion("brms")),
    backend = backend,
    fit_mode = "bayes_individual",
    criteria_mode = criteria_mode,
    K = K,
    n_chains = n_chains,
    n_cores = n_cores,
    n_iter = n_iter,
    n_warmup = n_warmup,
    seed = seed,
    empty = FALSE,
    save_fits = save_fits,
    choice_types_requested = as.list(choice_types),
    choice_types = as.list(prep_meta$choice_types),
    n_trials = nrow(d),
    n_participants = length(unique(units$participant)),
    n_fit_units = nrow(units),
    n_fitted = length(effect_rows),
    n_failed = length(fail),
    failed_units = as.list(fail),
    formula = paste(deparse(f), collapse = " "),
    preparation = prep_meta,
    note = paste(
      "Per-participant Bayesian fits (hmetad), one unit per participant × choiceType.",
      "Legacy hierarchical: scripts/r/_old/fit_hmeta_d_hierarchical.R;",
      "legacy MLE: scripts/_old/fit_hmeta_d_mle.py"
    ),
    outputs = list(
      subject_summary = "subject_summary.csv",
      group_summary = "group_summary.csv",
      subject_effects = "subject_effects.csv",
      cell_mratio_summary = "cell_mratio_summary.csv",
      convergence_qc = "convergence_qc.csv"
    )
  )
  write_json(meta, file.path(out_dir, "meta.json"), auto_unbox = TRUE, pretty = TRUE)
  progress(sprintf(
    "[%s] done -> %s (fitted %d / %d; failed %d)",
    dataset, out_dir, length(effect_rows), nrow(units), length(fail)
  ))
  invisible(out_dir)
}

# ---- main ----------------------------------------------------------------

.is_rscript <- function() {
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
    max_subjects = opts$max_subjects,
    save_fits = opts$save_fits,
    choice_types = opts$choice_types
  )
} else if (interactive() && !length(commandArgs(trailingOnly = TRUE))) {
  message(
    "Loaded fit_hmeta_d.R (Bayesian individual). In RStudio call e.g.\n",
    "  run_fit_hmeta_d(dataset = \"exp1a\", empty = TRUE, max_subjects = 2L)\n",
    "Or: Rscript scripts/r/fit_hmeta_d.R --dataset exp1a"
  )
}
