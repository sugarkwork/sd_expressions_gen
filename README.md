# sd_expressions_gen

This script automatically generates multiple facial expressions for a character by executing the API of the Stable Diffusion Web UI.

Install the required modules as follows:

```
pip install requests pillow
```

To configure Stable Diffusion Web UI, edit the webui-user.bat file and specify/add "--api" to the COMMANDLINE_ARGS.
```
@echo off

set PYTHON=
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS=--api
call webui.bat
```

Launching StableDiffusion.

When you run the script, it automatically starts writing a character using the StableDiffusion API.
It saves a file for each facial expression of the character.

```
python expressions_gen.py
```

## code

Define the base_prompt variable to specify the fundamental prompt for the character. You can use StableDiffusion-defined components such as LoRA and embeddings.

```
    base_prompt = ", 1girl, tareme, blonde hair, ponytail, blue eyes, masterpiece, high quality, cute, "\
                  "highres, delicate, beautiful detailed, finely detailed, front light, " \
                  "white background, standing, sfw, looking at viewer, (upper body:1.1),
```

All information such as the step number is stored in the payload variable.

## process
This code functions as follows.
1. Load the image to be set as the input for ControlNet.
2. Generate a character based on the specified prompt.
3. Blur the face of the generated character according to the mask.png.
4. Feed the blurred image into ControlNet and perform i2i to change the expression prompt.
