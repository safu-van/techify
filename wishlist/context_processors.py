from wishlist.models import Wishlist


# Get the count of Wishlist Items
def wishlist_items_count(request):
    user_id = request.user.id
    wishlist_count = Wishlist.objects.filter(user_id=user_id).count()
    return {"wishlist_count": wishlist_count}
