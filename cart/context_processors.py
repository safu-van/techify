from cart.models import CartItems

def cart_items_count(request):
    user_id = request.user.id
    count = CartItems.objects.filter(user_id=user_id).count()
    return {'count': count}