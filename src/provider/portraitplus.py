from .huggingface import BaseHFProvider

class PortraitPlusProvider(BaseHFProvider):
    name = "Portrait Plus"
    slug = "portraitplus"
    model = "wavymulder/portraitplus"