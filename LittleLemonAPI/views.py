from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
# from rest_framework.permissions import IsAdminUser
from .models import Category, Order, OrderItem, MenuItem, Cart,  User
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer
# from rest_framework import generics
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.authentication import SessionAuthentication
from django.contrib.auth.models import Group
# Create your views here.
# class-based views


class MenuItems(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, menuItem=None):
        try:
            if menuItem is not None:
                menu_item = MenuItem.objects.get(pk=menuItem)
                serialized_item = MenuItemSerializer(menu_item)
                return Response(serialized_item.data, status=status.HTTP_200_OK)
            else:
                menu_items = MenuItem.objects.all()
                serialized_items = MenuItemSerializer(menu_items, many=True)
                return Response(serialized_items.data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Menu item does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, menuItem=None):
        serializer = MenuItemSerializer(data=request.data)
        if request.user.groups.filter(name="Manager").exists():
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # only managers allowed to create menu items
            return Response({"message": "You are not authorised to perform this action"}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, menuItem=None):
        try:
            if request.user.groups.filter(name="Manager").exists():
                if menuItem is not None:
                    menu_item = MenuItem.objects.get(pk=menuItem)
                    serializer = MenuItemSerializer(
                        menu_item, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"message": "You are not authorized to perform this action"}, status=status.HTTP_403_FORBIDDEN)

        except MenuItem.DoesNotExist:
            return Response({"message": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, menuItem):

        try:
            if request.user.groups.filter(name="Manager").exists():
                if menuItem is not None:
                    menu_item = MenuItem.objects.get(pk=menuItem)
                    serializer = MenuItemSerializer(
                        menu_item, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"message": "You are not authorized to perform this action"}, status=status.HTTP_403_FORBIDDEN)

        except MenuItem.DoesNotExist:
            return Response({"message": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, menuItem):
        try:
            menu_item = MenuItem.objects.get(pk=menuItem)
            menu_item.delete()
            return Response({"message": "Menu item deleted"}, status=status.HTTP_200_OK)
        except MenuItem.DoesNotExist:
            return Response({"message": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)


class UserGroupManager(APIView):

    def get(self, request, userId=None):

        try:
            url_name = request.resolver_match.url_name
            # print("URL name:", url_name) #used for testing
            if request.user.groups.filter(name="Manager").exists():
                manager_group = Group.objects.get(name="Manager")
                crew_group = Group.objects.get(name="Delivery crew")
                if userId is not None:
                    user_to_get = User.objects.get(pk=userId)
                    if user_to_get.groups.filter(name="Manager").exists():
                        manager = manager_group.user_set.get(pk=userId)
                        serialized_item = UserSerializer(manager)
                        return Response(serialized_item.data, status=status.HTTP_200_OK)
                    elif user_to_get.groups.filter(name="Delivery crew").exists():
                        crew = crew_group.user_set.get(pk=userId)
                        serialized_item = UserSerializer(crew)
                        return Response(serialized_item.data, status=status.HTTP_200_OK)
                    else:
                        return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    if url_name == "managers":
                        managers = manager_group.user_set.all()
                        serialized_items = UserSerializer(managers, many=True)
                        return Response(serialized_items.data, status=status.HTTP_200_OK)
                    elif url_name == "delivery-crews":
                        crews = crew_group.user_set.all()
                        serialized_items = UserSerializer(crews, many=True)
                        return Response(serialized_items.data, status=status.HTTP_200_OK)
                    else:
                        return Response({"error": "Invalid url"}, status=status.HTTP_400_BAD_REQUEST)
        except Group.DoesNotExist:
            return Response({"error": "Manager group does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, userId=None):
        """Add a new member to the Manager or Delivery Crew group"""
        try:
            url_name = request.resolver_match.url_name
            if request.user.groups.filter(name="Manager").exists():
                if url_name == "managers":
                    group_name = "Manager"
                elif url_name == "delivery-crews":
                    group_name = "Delivery crew"
                else:
                    return Response({"error": "Invalid URL"}, status=status.HTTP_400_BAD_REQUEST)

                group = Group.objects.get(name=group_name)

                request_data = request.data.copy()
                request_data['groups'] = [group.id]
                # print(request_data)
                serializer = UserSerializer(data=request_data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "You are not authorized"}, status=status.HTTP_403_FORBIDDEN)
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, userId=None):
        try:
            url_name = request.resolver_match.url_name
            if request.user.groups.filter(name="Manager").exists():
                try:
                    user_to_delete = User.objects.get(pk=userId)
                    if url_name == "manager":
                        if user_to_delete.groups.filter(name="Manager").exists():
                            user_to_delete.delete()
                            return Response({"message": "Manager deleted"}, status=status.HTTP_200_OK)
                        else:
                            return Response({"error": "User does not belong to Manager"}, status=status.HTTP_404_NOT_FOUND)
                    elif url_name == "delivery-crews":
                        if user_to_delete.groups.filter(name="Delivery crew").exists():
                            user_to_delete.delete()
                            return Response({"message": "Delivery crew member deleted"}, status=status.HTTP_200_OK)
                        else:
                            return Response({"error": "User does not belong to Delivery crew"}, status=status.HTTP_404_NOT_FOUND)
                except User.DoesNotExist:
                    return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "You are not authorized to perform this action"}, status=status.HTTP_403_FORBIDDEN)
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)


class CartItems(APIView):
    def get(self, request):
        try:
            cart_items = Cart.objects.filter(user=request.user)
            serialized_items = CartSerializer(cart_items, many=True)
            return Response(serialized_items.data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"message": "There is no item in cart"}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        try:
            menuitem_id = request.data.get('menuitem')
            quantity = request.data.get('quantity')

            # Create a new cart item
            cart_item_data = {
                'user': request.user.id,
                'menuitem': menuitem_id,
                'quantity': quantity,
                # price and unit price is set dynamically
            }
            serializer = CartSerializer(data=cart_item_data)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({"message": "There is nothing to add in cart"}, status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request):
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items.exists():
                cart_items.delete()
                return Response({"message": "Cart items deleted"}, status=status.HTTP_200_OK)
            return Response({"message": "Cart item is empty"}, status=status.HTTP_404_NOT_FOUND)
        except MenuItem.DoesNotExist:
            return Response({"error": "Cart item does not exist"}, status=status.HTTP_404_NOT_FOUND)


class Order(APIView):
    pass


@api_view(["GET"])
# @authentication_classes([SessionAuthentication]) // enabling it allows browsable api to remove token based auth meant for dev testing (temporary)
# @permission_classes([IsAuthenticated]) // SessionAuthentication must be enable in settings
def endpoints(request):
    return Response(
        {"Menu-items":
         {"endpoints": ["/api/menu-items", r"/api/menu-items/{menuItem}"], "methods": {
             "Customer, delivery crew": "GET", "Manager": "GET, POST, PUT, PATCH, DELETE"
         }}, "User group": {"endpoints": ["/api/groups/manager/users", r"/api/groups/manager/users/{userId}", "/api/groups/delivery-crew/users", r"/api/groups/delivery-crew/users/{userId}"], "methods": {
             "Manager": "GET, POST, PUT, PATCH, DELETE"
         }}, "Cart": {"endpoints": ["/api/cart/menu-items"], "methods": {"Customer": "GET, POST, DELETE"}},
            "Order": {"endpoints": ["/api/orders", r"/api/orders/{orderId}"], "methods": {
                "Customer": "GET, POST, PUT, PATCH",  "Manager": "GET, DELETE", "Delivery crew": "GET, PATCH"
            }}, "role": ["Customer", "delivery crew", "Manager"], "User registration": {
             "methods": "GET POST", "role": "valid creditiontials", "endpoints": [
                "/api/users", "/token/login/", "/api/users/me/"
             ]

         }}, status=status.HTTP_200_OK)
