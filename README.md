# sd_expressions_gen

This script automatically generates multiple facial expressions for a character by executing the API of the Stable Diffusion Web UI.

Right now, it's just a matter of calling the API of the Web UI from the script.
I would like to implement it as an extension of the Stable Diffusion Web UI in the future.

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

A list of facial expressions is defined in the "expressions" variable.
If there are unnecessary facial expressions, you can delete or add them.
The key will be the filename and the value will be the actual prompt.

## process
This code functions as follows.
1. Load the image (cn.png) to be set as the input for ControlNet.
2. Generate a character based on the specified prompt.

![expressionless](https://user-images.githubusercontent.com/98699377/229041913-63d2da6a-4813-4d28-9c73-c05a6a817f59.png)

4. Blur the face of the generated character according to the mask.png.

![br](https://user-images.githubusercontent.com/98699377/229041924-2c6aea6d-0045-4822-b552-0f8eb94bfe66.png)

5. Feed the blurred image into ControlNet and perform i2i to change the expression prompt.

![smile](https://user-images.githubusercontent.com/98699377/229041920-aee011e5-e6dc-439f-8c92-74d084862eec.png)

Repeats the process for the number of expressions defined in the "expressions" variable.

If you prepare a pose image (cn.png) for ControlNet and a face mask (mask.png), you can easily create a standing image that can be used in the game.

## facial expressions sample

https://ai.sugar-knight.com/aitest/ex.html

## why did i make this
If we were to create a game in which AI dynamically prepares scenarios and character images, we thought it would be better to automatically generate the character's facial expressions. We verified the implementation of character facial expressions using only the API without going through the Web UI.

## future plans
 - Automatically create a face mask image (mask.png) from an image for ControlNet.
 - Create a costume change sample.
 - Make it an extension of the web UI.
