from rest_framework.routers import DefaultRouter

from .api import OrderViewSet, ProductViewSet

router = DefaultRouter()
router.register('productos', ProductViewSet, basename='producto')
router.register('pedidos', OrderViewSet, basename='pedido')

urlpatterns = router.urls