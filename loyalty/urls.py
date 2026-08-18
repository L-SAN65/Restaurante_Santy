from django.urls import path

from .views import redeem_view, wallet_view

app_name = "loyalty"

urlpatterns = [
    path("", wallet_view, name="wallet"),
    path("canjear/", redeem_view, name="redeem"),
]