from apps._reporting.endpoints import build_urlpatterns_for_registry
from .registry import REGISTRY


urlpatterns = build_urlpatterns_for_registry(REGISTRY)
