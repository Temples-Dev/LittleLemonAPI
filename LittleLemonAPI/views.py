from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from .models import Category, Order as OrderModel, OrderItem, MenuItem, Cart,  User
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth.models import Group
from django.db import transaction
from datetime import datetime
from rest_framework.exceptions import PermissionDenied, NotFound
# Create your views here.


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
                category_name = request.query_params.get("category")
                to_price = request.query_params.get("price")
                if category_name:
                   menu_items= menu_items.filter(category__title= category_name)
                if to_price:
                   menu_items= menu_items.filter(price__lte= to_price)
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

    def get(self, request, orderId=None):
        try:
            url_name = request.resolver_match.url_name

            if url_name == "orders":
                user = request.user

                # Check if the user is a member of the Manager group
                if user.groups.filter(name="Manager").exists():
                    # Return all orders with order items by all users
                    orders = OrderModel.objects.all()

                # Check if the user is a member of the Delivery crew group
                elif user.groups.filter(name="Delivery crew").exists():
                    # Return all orders with order items assigned to the delivery crew
                    orders = OrderModel.objects.filter(delivery_crew=user)

                # Default behavior for customer
                else:
                    # Return orders with order items for the current user
                    orders = OrderModel.objects.filter(user=user)

                # Serialize the queryset and return the response
                serialized_orders = OrderSerializer(orders, many=True)
                return Response(serialized_orders.data, status=status.HTTP_200_OK)
            elif url_name == "order-item":
                # Customer GET: Returns all items for this order id.
                # If the order ID doesn’t belong to the current user, return 404.
                # order_id = orderId
                order = OrderModel.objects.get(id=orderId, user=request.user)
                print("order checking", order)
                # order_items = OrderItem.objects.filter(order=order)
                # serialized_order_items = OrderItemSerializer(
                #     order_items, many=True)
                serialized_order_item = OrderSerializer(order)
                return Response(serialized_order_item.data, status=status.HTTP_200_OK)
        except OrderModel.DoesNotExist:
            return Response({'message': "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("something went wrong", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, orderId=None):
        # Begin a transaction to ensure data consistency
        try:
            with transaction.atomic():
                # Fetch cart items for the user
                cart_items = Cart.objects.filter(user=request.user)

                # Check if the cart is empty
                if not cart_items:
                    return Response({'error': 'Cart is empty. Cannot create an order with an empty cart.'}, status=status.HTTP_400_BAD_REQUEST)

                total = 0
                date = datetime.now()
                # Create the Order instance
                order = OrderModel.objects.create(
                    user=request.user,
                    total=total,
                    date=date.strftime('%Y-%m-%d')

                )

                # Iterate through each item in the cart and create an OrderItem
                order_items = []
                for cart_item in cart_items:

                    # Create OrderItem instances associated with the newly created Order
                    order_item_data = {
                        "order": order.id,
                        "menuitem": cart_item.menuitem.id,
                        "quantity": cart_item.quantity,
                        "unitprice": cart_item.unitprice,
                        "price": cart_item.price
                    }
                    order_items.append(order_item_data)

                # Serialize the list of OrderItem instances
                print(order_items)
                order_serializer = OrderItemSerializer(
                    data=order_items, many=True)

                if order_serializer.is_valid(raise_exception=True):
                    # Save order items to the database
                    order_serializer.save()

                    # Delete all items from the cart for this user
                    cart_items.delete()

                    return Response({'message': 'Order created successfully.'}, status=status.HTTP_201_CREATED)
                else:
                    return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def put(self, request, orderId=None):
    #     try:
    #         url_name = request.resolver_match.url_name

    #         if url_name == "order-item":
    #             user = request.user

    #             # Retrieve the order instance
    #             order = OrderModel.objects.get(pk=orderId)
    #             print("Put Order is", order)

    #             # Ensure the user owns the order
    #             if order.user != user:
    #                 return Response({"message": "You are not authorized to perform this action"}, status=status.HTTP_403_FORBIDDEN)

    #             # Serialize the updated order data
    #             serializer = OrderSerializer(order, data=request.data)
    #             if serializer.is_valid():
    #                 serializer.save()
    #                 return Response(serializer.data, status=status.HTTP_200_OK)
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #     except OrderModel.DoesNotExist:
    #         return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
                
                
            
        except Exception as e:
            print("something went wrong",e)

    def patch(self, request, orderId=None):
        try:
            url_name = request.resolver_match.url_name
            if url_name == "order-item":
                user = request.user

                order = OrderModel.objects.get(pk=orderId)
                # Check if the user is a member of the Delivery crew group
                if user.groups.filter(name="Delivery crew").exists():
                  

                    # Ensure the delivery crew member can only update the order status
                    if 'status' in request.data:
                        order.status = request.data['status']
                        order.save()
                        return Response({'message': 'Order status updated successfully.'}, status=status.HTTP_200_OK)
                    else:
                        raise PermissionDenied("Delivery crew members can only update the order status.")

                
                
                # Check if the user is a member of the Manager group
                elif user.groups.filter(name="Manager").exists():
                    
                    
                    # Manager can update order status and set delivery crew
                    if 'status' in request.data:
                        order.status = request.data['status']

                    if 'delivery_crew' in request.data:
                        delivery_crew_id = request.data['delivery_crew']
                        try:
                            delivery_crew = User.objects.get(id=delivery_crew_id)
                            # Check if the user is a member of the Delivery crew group
                            if not delivery_crew.groups.filter(name="Delivery crew").exists():
                                raise PermissionDenied("Assigned user is not a delivery crew member.")
                            order.delivery_crew = delivery_crew
                        except User.DoesNotExist:
                            raise NotFound("Delivery crew not found.")

                    order.save()
                   
                    return Response({'message': 'Order updated successfully.'}, status=status.HTTP_200_OK)

                else:
                    raise PermissionDenied("You're not authorised to update order details.")

        except OrderModel.DoesNotExist:
            raise NotFound("Order not found.")
        except Exception as e:
            print("Something went wrong", e)
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, orderId=None):
        url_name = request.resolver_match.url_name
        if url_name == "order-item":
            user = request.user
            try:
                if user.groups.filter(name="Manager").exists():
                    # Return all orders with order items by all users
                    order_item = OrderModel.objects.get(pk=orderId)
                    order_item.delete()
                    return Response({"message": "Order deleted successfully"}, status=status.HTTP_200_OK)
                return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
            except OrderModel.DoesNotExist:
                return Response({"error": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
# enabling it allows browsable api to remove token based auth meant for dev testing (temporary)
@authentication_classes([SessionAuthentication])
# SessionAuthentication must be enable in settings
@permission_classes([IsAuthenticated])
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
