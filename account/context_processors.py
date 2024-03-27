from authentication.models import User
from django.core.exceptions import ObjectDoesNotExist

def user_name(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            pass
        name = user.name
        return {'name': name}
    return {'name': None}