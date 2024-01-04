import replicate

def generate_music(prompt: str, duration: int = 33) -> str:
    """
    Generate music based on a text prompt using Replicate API.

    Args:
        prompt (str): The text prompt to guide the music generation.
        duration (int, optional): The duration of the music in seconds. Default is 33.

    Returns:
        str: The URL of the generated music file.
    """

    # Configure the Replicate API call
    output = replicate.run(
        "meta/musicgen:b05b1dff1d8c6dc63d14b0cdb42135378dcb87f6373b0d3d341ede46e59e2b38",
        input={
            "top_k": 250,
            "top_p": 0,
            "prompt": prompt,
            "duration": duration,
            "temperature": 1,
            "continuation": False,
            "model_version": "stereo-large",
            "output_format": "wav",
            "continuation_start": 0,
            "multi_band_diffusion": False,
            "normalization_strategy": "peak",
            "classifier_free_guidance": 3
        }
    )

    # Extract and return the URL of the generated music file
    music_url = output.get('output')
    return music_url

# Example usage
prompt = "Edo25 major g melodies that sound triumphant and cinematic. Leading up to a crescendo that resolves in a 9th harmonic"
music_url = generate_music(prompt)
print(music_url)
