from .huggingface import BaseHFProvider

class NitroDiffusionProvider(BaseHFProvider):
    name = "Nitro Diffusion"
    slug = "nitrodiffusion"
    model = "nitrosocke/Nitro-Diffusion"