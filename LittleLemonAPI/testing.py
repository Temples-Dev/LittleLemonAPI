 def get(self, request, orderId=None):
        if orderId:
            return self.retrieve(request, orderId)
        else:
            return self.list(request)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, orderId):
        queryset = self.get_queryset()
        order = queryset.filter(pk=orderId).first()
        if not order:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            cart_items = Cart.objects.filter(user=self.request.user)
            total = self.calculate_total(cart_items)
            order = serializer.save(user=self.request.user, total=total)

            for cart_item in cart_items:
                OrderItem.objects.create(menuitem=cart_item.menuitem, quantity=cart_item.quantity,
                                         unit_price=cart_item.unit_price, price=cart_item.price, order=order)
                cart_item.delete()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def calculate_total(self, cart_items):
        total = Decimal(0)
        for item in cart_items:
            total += item.price
        return total