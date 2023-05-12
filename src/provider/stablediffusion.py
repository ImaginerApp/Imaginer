from .huggingface import BaseHFProvider

class StableDiffusionProvider(BaseHFProvider):
    name = "Stable Diffusion"
    slug = "stablediffusion"
    model = "stabilityai/stable-diffusion-2-1"