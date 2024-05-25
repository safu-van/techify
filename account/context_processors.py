from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

from authentication.models import User


# Fetch the authenticated user name
def user_name(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        try:
            user_name = User.objects.filter(id=user_id).values_list('name', flat=True).first()
            return {"name": user_name}
        except ObjectDoesNotExist:
            return redirect("authentication:signin")
    return {"name": None}
