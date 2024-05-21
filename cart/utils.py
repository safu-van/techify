from account.models import Wallet, WalletTransaction
from product.models import Product
from cart.models import CartItems


# Withdraw money from wallet (when user purchase using wallet)
def withdraw_from_wallet(user, total_amount):
    if total_amount == 0:
        return True
    if Wallet.objects.filter(user=user).exists():
        wallet = Wallet.objects.get(user=user)
        if wallet.amount >= total_amount:
            wallet.amount -= total_amount
            wallet.save()
            transaction = WalletTransaction.objects.create(
                wallet=wallet,
                description="Ordered Products",
                amount=total_amount,
                is_credit=False,
            )
            transaction.save()
            return True
        else:
            return False
    else:
        return False


# Update Wallet (when product is returned or cancelled)
def update_wallet(user, amount, description):
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
        is_credit=True,
    )
    transaction.save()


# To Check product stock
def check_product_stock(request):
    user_id = request.user.id
    products = CartItems.objects.filter(user=user_id)

    for product in products:
        qty = product.quantity
        stock = product.product.stock
        product_name = product.product.name
        if stock < qty:
            request.session["message"] = (
                f"Sorry, We only have { stock } quantity of { product_name }."
            )
            return False
    return True


# Update product stock (after product returned or cancelled)
def update_product_stock(purchased_qty, product_id):
    product = Product.objects.get(id=product_id)
    product.stock += purchased_qty
    product.save()
