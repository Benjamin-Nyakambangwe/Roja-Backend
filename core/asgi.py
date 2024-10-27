import os
import django

# Set settings module before anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# Initialize Django (this is crucial)
django.setup()

# Now import Django-related modules after initialization
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from api.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
