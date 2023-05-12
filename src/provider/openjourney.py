from .huggingface import BaseHFProvider

class OpenJourneyProvider(BaseHFProvider):
    name = "Open Journey"
    slug = "openjourney"
    model = "prompthero/openjourney-v4"