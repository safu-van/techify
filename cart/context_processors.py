from cart.models import CartItems


# Get the count of Cart Items
def cart_items_count(request):
    user_id = request.user.id
    cart_count = CartItems.objects.filter(user=user_id).count()
    return {"cart_count": cart_count}
