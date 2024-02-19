from django.urls import path

from .views import MenuItems, UserGroupManager,CartItems, Order,endpoints

urlpatterns = [
    # Menu-items endpoints
    path("", endpoints, name="all-endpoints"),
    path(r"menu-items", MenuItems.as_view() , name="menu-items"),
    path(r"menu-items/<int:menuItem>", MenuItems.as_view() , name="menu-item"),
    # User group management endpoints
    path(r"groups/manager/users", UserGroupManager.as_view(), name="managers"),
    path(r"groups/manager/users/<int:userId>", UserGroupManager.as_view(), name="manager" ),
    path(r"groups/delivery-crew/users", UserGroupManager.as_view(), name="delivery-crews"),
    path(r"groups/delivery-crew/users/<int:userId>", UserGroupManager.as_view(), name="delivery-crew"),
    # # Cart management endpoints 
    path(r"cart/menu-items", CartItems.as_view(), name= "cart"),
    # # Order management endpoints
    path(r"orders", Order.as_view(), name= "orders"),
    path(r"orders/<int:orderId>", Order.as_view() , name="order-item"),
]