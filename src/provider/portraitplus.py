from .huggingface import BaseHFProvider

class PortraitPlusProvider(BaseHFProvider):
    name = "Portrail Plus"
    slug = "portrailplus"
    model = "wavymulder/portraitplus"