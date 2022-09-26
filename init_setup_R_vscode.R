#!/usr/bin/env Rscript
#
#=============================================================================
# This is the R script for first-time setup of R to be used with VS Code
# Ref: https://github.com/ManuelHentschel/VSCode-R-Debugger
#=============================================================================

# First time setup script for R on Windows
pkg_list <- c(
    "languageserver",
    "httpgd",
    "tidyverse",
    "devtools"
)

install.packages(pkg_list, repos = "https://cloud.r-project.org")
print("Packages installation completed.")

# Github may not work as it could be blocked by proxy
devtools::install_github("ManuelHentschel/vscDebugger")
