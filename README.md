# sd_expressions_gen

This script automatically generates multiple facial expressions for a character by executing the API of the Stable Diffusion Web UI.

Install the required modules as follows:

```
pip install requests pillow
```

Modify the settings of Stable Diffusion as follows:
To configure Stable Diffusion Web UI, edit the webui-user.bat file and specify/add "--api" to the COMMANDLINE_ARGS.

ex)
```
@echo off

set PYTHON=
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS=--api
call webui.bat
```
