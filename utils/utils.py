import magic

from account.models import Wallet, WalletTransaction
from product.models import Product


# To validate image
def validate_image(image):
    mime = magic.Magic(mime=True)
    image_mime = mime.from_buffer(image.read())

    allowed_mimes = ["image/jpeg", "image/png", "image/gif"]

    if image_mime not in allowed_mimes:
        return False
    return True


# Update Wallet
def update_wallet(user, amount, description, is_credit):
    if Wallet.objects.filter(user=user).exists():
        wallet = Wallet.objects.get(user=user)
        wallet.amount += amount
    else:
        wallet = Wallet.objects.create(user=user, amount=amount)
    wallet.save()
    transaction = WalletTransaction.objects.create(
        wallet=wallet,
        description=description,
        amount=amount,
        is_credit=is_credit,
    )
    transaction.save()


# Update product stock 
def update_product_stock(purchased_qty, product_id):
    product = Product.objects.get(id=product_id)
    product.stock += purchased_qty
    product.save()