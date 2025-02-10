#!/usr/bin/env bash

# Init
venv_name="qva_dev"
txt_path=$(PWD)"/dev.txt"
py_version="Python311"

# Create a virtual environment
mkdir /c/pythonEnv
cd /c/pythonEnv
$LOCALAPPDATA/Programs/Python/$py_version/python.exe -m venv $venv_name
/c/$py_version/python.exe -m venv $venv_name
source $venv_name/Scripts/activate

# Install all necessary python packages. -U to upgrade if possible
python -m pip install -U pip
python -m pip install -U -r $txt_path