#!/usr/bin/env Rscript
#
# DEPRECATED stub — Bayesian individual meta-d' moved to:
#   scripts/r/fit_hmeta_d.R
#
# This file remains so old paths keep working.

args <- commandArgs(trailingOnly = FALSE)
file_arg <- sub("^--file=", "", grep("^--file=", args, value = TRUE))
here <- if (length(file_arg)) dirname(normalizePath(file_arg[[1]])) else getwd()
target <- normalizePath(file.path(here, "..", "fit_hmeta_d.R"), mustWork = TRUE)
message("NOTE: scripts/r/_old/fit_hmeta_d_bayes_indiv.R is deprecated; using ", target)
cmd_args <- commandArgs(trailingOnly = TRUE)
status <- system2("Rscript", c(target, cmd_args))
quit(status = if (is.null(status) || is.na(status)) 0L else as.integer(status))
