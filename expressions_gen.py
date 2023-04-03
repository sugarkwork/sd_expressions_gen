import base64
import io
import requests
from PIL import Image, ImageFilter
import os
import yaml

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
config = yaml.safe_load(open(os.path.join(SCRIPT_DIR, "config.yaml"), "r"))


class FaceGenerator:
    def __init__(self, base_url=config["base_url"], base_prompt="1girl"):
        self.base_url = base_url
        self.base_prompt = base_prompt

    @staticmethod
    def base64_image(img):
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        byte_array = buffered.getvalue()
        buffered.close()
        return base64.b64encode(byte_array).decode("utf-8")

    @staticmethod
    def base64_file(filename):
        with open(filename, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")

    def get_controlnet_models(self, model_filter=None):
        response = requests.get(url=f"{self.base_url}/controlnet/model_list")
        model_list = response.json()["model_list"]
        if not model_filter:
            return model_list
        else:
            return [item for item in model_list if model_filter in item]

    def get_checkpoint_models(self, model_filter=None):
        response = requests.get(url=f"{self.base_url}/sdapi/v1/sd-models")
        model_list = response.json()
        if not model_filter:
            return model_list
        else:
            return [item for item in model_list if model_filter in item.get('title')]

    def refresh_checkpoints(self):
        response = requests.post(url=f"{self.base_url}/sdapi/v1/refresh-checkpoints")

    def set_checkpoints(self, checkpoints, vae):
        payload = {
            "sd_model_checkpoint": checkpoints,
            "sd_vae": vae
        }
        response = requests.post(url=f"{self.base_url}/sdapi/v1/options", json=payload)

    def generate_face(self, expression, mode="t2i", init_img=None, control_img=None):
        if not control_img:
            control_img = self.base64_file(config["controlnet_base"])
        else:
            control_img = self.base64_image(control_img)

        payload = {
            "prompt": f"{expression}, {self.base_prompt}",
            "negative_prompt": "(worst quality, low quality:1.4), nsfw, nipples, pussy",
            "sampler_name": "DPM++ SDE Karras",
            "steps": 15,
            "cfg_scale": 5.5,
            "batch_count": 1,
            "batch_size": 1,
            "filter_nsfw": False,
            "include_grid": False,
            "width": 480,
            "height": 640,
            "enable_hr": False,
            "denoising_strength": 0.65,
            "hr_scale": 1.3,
            "controlnet_units": [
                {
                    "input_image": control_img,
                    "module": "openpose",
                    "model": self.get_controlnet_models('openpose')[0],
                    "weight": 1
                }
            ],
        }

        if mode == "i2i":
            payload["controlnet_units"].append({
                "module": "canny",
                "model": self.get_controlnet_models('canny')[0],
                "weight": 0.8
            })

        if init_img:
            payload["init_images"] = [self.base64_image(init_img)]

        path = "/controlnet/txt2img" if mode == "t2i" else "/controlnet/img2img"
        response = requests.post(url=f"{self.base_url}{path}", json=payload)
        result = response.json()

        for i in result["images"]:
            image = Image.open(io.BytesIO(
                base64.b64decode(i.split(",", 1)[0])))
            return image

    @staticmethod
    def create_blurred_image(img):
        mask = Image.open(config["mask"]).convert("L")
        blurred = img.filter(ImageFilter.GaussianBlur(radius=20))
        result = Image.composite(img, blurred, mask)
        return result


def main():
    output_dir = SCRIPT_DIR
    if os.path.isabs(config["output_dir"]):
        output_dir = config["output_dir"]
    else:
        output_dir = os.path.join(SCRIPT_DIR, config["output_dir"])
    os.makedirs(output_dir, exist_ok=True)

    base_prompt = config["prompt"]

    face_generator = FaceGenerator(base_prompt=base_prompt)
    face_generator.refresh_checkpoints()
    sd_model = face_generator.get_checkpoint_models(config["sd_model"])[0]['title']
    face_generator.set_checkpoints(sd_model, config["sd_vae"])

    new_img = face_generator.generate_face("expressionless")
    new_img.save(f"{output_dir}/expressionless.png")

    blurred_img = face_generator.create_blurred_image(new_img)

    expressions = {
        'smile': 'smile',
        'crazy': 'emptiness, (empty eyes:1.2), (blank eyes:1.2), (dilated pupils:1.2), open mouth',
        'sleepy': 'drooping eyelids, droopy eyes, sleepy eyes, bedroom eyes, half-closed eyes',
        'painful': 'clenched teeth, one eye closed, sad',
        'endure pain': 'open mouth, half-closed eyes, (sad:1.1), sweat',
        'evil smile': 'evil smile',
        'heart': '(heart-shaped pupils:1.3), blush, heart, heart-shaped eyes',
        'angry': '(angry:0.7)',
        'happy': 'happy',
        'sad': '(sad:1.2), half-closed eyes',
        'crying': 'crying, tears',
        'bawl': 'crying, (closed eyes:1.3), (tears:1.1), open mouth, sad',
        'confused': 'confused',
        'scared': 'scared, open mouth',
        'surprised': 'wide-eyed, open mouth, surprised, ',
        'laughing': 'laughing',
        'closed eyes': '(closed eyes:1.3)',
        'half-closed eyes': 'half-closed eyes',
        'excitement': 'orgasm, blush',
        'shy': 'blush, shy',
        'shouting': 'shouting',
        'kiss': '(kiss:1.1), (closed eyes:1.3)',
        'ahegao soft': '(ahegao:1.2), blush, (tongue out:1.1), open mouth, sweat',
        'ahegao hard': '(ahegao:1.2), blush, (tongue out:1.1), open mouth, sweat, rolling eyes',
        'ahegao with heart': '(ahegao:1.2), blush, (tongue out:1.1), open mouth, sweat, heart-shaped pupils, '
                             'heart-shaped eyes',
        'wink': 'one eye closed',
        'get drunk': 'blush, open mouth, sweat',
    }

    mask = Image.open("mask.png").convert("L")

    for expression in expressions.keys():
        img = face_generator.generate_face(
            expressions.get(expression) + base_prompt,
            mode="i2i",
            init_img=blurred_img,
            control_img=blurred_img,
        )
        result = Image.composite(blurred_img, img, mask)
        result.save(f"{output_dir}/{expression}.png")


if __name__ == "__main__":
    main()

# EOF
