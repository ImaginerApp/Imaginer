from .analogdiffusion import AnalogDiffusionProvider
from .anything import AnythingProvider
from .custom import CustomProvider
from .nitrodiffusion import NitroDiffusionProvider
from .openai import OpenAIProvider
from .openjourney import OpenJourneyProvider
from .portraitplus import PortraitPlusProvider
from .stablediffusion import StableDiffusionProvider
from .stablediffusionlocal import StableDiffusionLocalProvider
from .waifudiffusion import WaifuDiffusionProvider

PROVIDERS = {
    "analogdiffusion": AnalogDiffusionProvider,
    "anything": AnythingProvider,
    "custom": CustomProvider,
    "nitrodiffusion": NitroDiffusionProvider,
    "openai": OpenAIProvider,
    "openjourney": OpenJourneyProvider,
    "portraitplus": PortraitPlusProvider,
    "stablediffusion": StableDiffusionProvider,
    "stablediffusionlocal": StableDiffusionLocalProvider,
    "waifudiffusion": WaifuDiffusionProvider,
}
