from .huggingface import BaseHFProvider

class PortraitPlusProvider(BaseHFProvider):
    name = "Portrait Plus"
    slug = "portraitlplus"
    model = "wavymulder/portraitplus"