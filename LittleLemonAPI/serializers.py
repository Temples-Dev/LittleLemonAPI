from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import MenuItem, Cart, Category, Order, OrderItem, User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = "__all__"
        depth = 1


class CartSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = Cart
        fields = "__all__"
        

    def get_price(self, cart: Cart):
        return cart.quantity * cart.unitprice


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[
                                   UniqueValidator(queryset=User.objects.all())], write_only=True)

    password = serializers.CharField(
        required=True, min_length=8, write_only=True, validators=[validate_password])

    first_name = serializers.CharField(
        required=True, max_length=150, write_only=True)
    last_name = serializers.CharField(
        required=True, max_length=150, write_only=True)

    class Meta:

        model = User
        fields = ['id', 'username', 'password', "first_name",
                  "last_name", "email", "groups"]

        extra_kwargs = {  # extra_kwargs
            'id': {
                "read_only": True
            },
            'groups': {
                'write_only': True
            }

        }

    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
