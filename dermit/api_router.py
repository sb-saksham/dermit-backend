from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter


from chat.api.views import ConversationViewSet, MessageViewSet, UserViewSet, ImageViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("conversations", ConversationViewSet)
router.register("users", UserViewSet)
router.register("messages", MessageViewSet)
router.register("images", ImageViewSet, basename="images")


app_name = "api"

urlpatterns = router.urls
