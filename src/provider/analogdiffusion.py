from .huggingface import BaseHFProvider

class AnalogDiffusionProvider(BaseHFProvider):
    name = "Analog Diffusion"
    slug = "analogdiffusion"
    model = "wavymulder/Analog-Diffusion"