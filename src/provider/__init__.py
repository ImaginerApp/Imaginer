from .analogdiffusion import AnalogDiffusionProvider
from .anything import AnythingProvider
from .nitrodiffusion import NitroDiffusionProvider
from .openai import OpenAIProvider
from .openjourney import OpenJourneyProvider
from .portraitplus import PortraitPlusProvider
from .stablediffusion import StableDiffusionProvider
from .waifudiffusion import WaifuDiffusionProvider

PROVIDERS = {
    "analogdiffusion": AnalogDiffusionProvider,
    "anything": AnythingProvider,
    "nitrodiffusion": NitroDiffusionProvider,
    "openai": OpenAIProvider,
    "openjourney": OpenJourneyProvider,
    "portraitplus": PortraitPlusProvider,
    "stablediffusion": StableDiffusionProvider,
    "waifudiffusion": WaifuDiffusionProvider,
}
