from .huggingface import BaseHFProvider

class WaifuDiffusionProvider(BaseHFProvider):
    name = "Waifu Diffusion"
    slug = "waifudiffusion"
    model = "hakurei/waifu-diffusion"