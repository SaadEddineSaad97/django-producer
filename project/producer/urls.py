from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, WebhookReceiverView

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/webhook/', WebhookReceiverView.as_view(), name='webhook-receiver'),
]
