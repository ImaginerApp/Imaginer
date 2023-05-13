from .huggingface import BaseHFProvider

class PortraitPlusProvider(BaseHFProvider):
    name = "Portrait Plus"
    slug = "portrailplus"
    model = "wavymulder/portraitplus"