@echo off
::=============================================================================
:: This is the common batch script for first-time setup of conda environment
:: Ref: https://www.dunderdata.com/blog/anaconda-is-bloated-set-up-a-lean-robust-data-science-environent-with-miniconda-and-conda-forge
::=============================================================================

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: VARIABLES
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

setlocal

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: COMMANDS
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

call conda activate base
call conda env config vars set MAMBA_NO_BANNER=1
call conda activate base

:: Data science utilities - install at user level, available across envs
:: Utils for project template creation and updating
call pip install --user cookiecutter
call pip install --user cruft

:: Use mamba in place of conda
call conda install mamba -n base -c conda-forge
call mamba create -n minimal_ds

rem Checks whether the env has been created in the expected path
set path_to_check=%USERPROFILE%\miniconda3\

if not exist %path_to_check% (
    echo "Environment folder does not exist."
    exit /b 1
)

rem Now proceeds to create the minimal data science environment
cd %path_to_check%

:: Disable mamba banner via env variable
call conda activate minimal_ds
call conda env config vars set MAMBA_NO_BANNER=1
call conda activate minimal_ds

:: Add and enforce the use of conda-forge as the preferred channel
call conda config --env --add channels conda-forge
call conda config --show channels
call conda config --env --set channel_priority strict
call conda config --show channel_priority

:: Install the basic required packages here
:: These are expected in every Python data science stack
call mamba install pandas scikit-learn matplotlib notebook seaborn
call mamba install jupyter jupyterlab

:: Additional Python packages
:: Allow running jupyter notebook against kernels in other conda environments
call mamba install nb_conda_kernels
::call mamba install scrapy

:: R data science stack
call mamba install r r-irkernel
call Rscript .\init_setup_R_vscode.R

:: Clean up
call conda deactivate

endlocal
