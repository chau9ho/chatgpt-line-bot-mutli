import replicate

class StableDiffusion:
    def __init__(self):
        self.prompt = "a vision of paradise. unreal engine"
    
    def get_url(self):
        model_identifier = "stability-ai/sdxl:c221b2b8ef527988fb59bf24a8b97c4561f1c671f73bd389f866bfb27c061316"
        input_data = {
            "width": 1024,
            "height": 1024,
            "prompt": self.prompt,  # Use the stored prompt instead of the default one
            "refine": "no_refiner",
            "scheduler": "K_EULER",
            "lora_scale": 0.6,
            "num_outputs": 1,
            "guidance_scale": 7.5,
            "apply_watermark": True,
            "high_noise_frac": 0.8,
            "negative_prompt": "",
            "prompt_strength": 0.8,
            "num_inference_steps": 50
        }

        output = replicate.run(model_identifier, input=input_data)

        output = str(output[0])  # Assuming the output is a list with a single URL
        output = output.replace("\'", "")
        output = output.replace("[", "")
        output = output.replace("]", "")

        return output

    def add_prompt(self, text):
        self.prompt = text
