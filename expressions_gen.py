import base64
import io
import requests
from PIL import Image, ImageFilter


class FaceGenerator:
    def __init__(self, base_url="http://127.0.0.1:7860", base_prompt="1girl"):
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

    def generate_face(self, expression, mode="t2i", init_img=None, control_img=None):
        if not control_img:
            control_img = self.base64_file("cn.png")
        else:
            control_img = self.base64_image(control_img)

        payload = {
            "sd_model": "anythingV5Anything_anythingV5PrtRE.safetensors",
            "prompt": expression + self.base_prompt,
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
                    "model": "control_sd15_openpose [fef5e48e]",
                    "weight": 1
                }
            ],
        }

        if mode == "i2i":
            payload["controlnet_units"][0].update({
                "module": "canny",
                "model": "control_sd15_canny [fef5e48e]",
                "weight": 0.8
            })

        if init_img:
            payload["init_images"] = [self.base64_image(init_img)]

        path = "/controlnet/txt2img" if mode == "t2i" else "/controlnet/img2img"
        response = requests.post(url=f"{self.base_url}{path}", json=payload)
        result = response.json()

        for i in result["images"]:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
            return image

    @staticmethod
    def create_blurred_image(img):
        mask = Image.open("mask.png").convert("L")
        blurred = img.filter(ImageFilter.GaussianBlur(radius=20))
        result = Image.composite(img, blurred, mask)
        return result


def main():
    base_prompt = ", 1girl, tareme, blonde hair, ponytail, blue eyes, masterpiece, high quality, cute, "\
                  "highres, delicate, beautiful detailed, finely detailed, front light, " \
                  "white background, standing, sfw, looking at viewer, (upper body:1.1), <lora:rykd:0.2>"
    face_generator = FaceGenerator(base_prompt=base_prompt)
    new_img = face_generator.generate_face("expressionless")
    new_img.save("expressionless.png")

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
        'ahegao with heart': '(ahegao:1.2), blush, (tongue out:1.1), open mouth, sweat, heart-shaped pupils, heart-shaped eyes',
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
        result.save(f"{expression}.png")


if __name__ == "__main__":
    main()

# EOF
