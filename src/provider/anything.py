from .huggingface import BaseHFProvider

class AnythingProvider(BaseHFProvider):
    name = "Anything"
    slug = "anything"
    model = "andite/anything-v4.0"