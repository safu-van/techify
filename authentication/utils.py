from authentication.models import User
from account.models import Wallet, WalletTransaction


# Add referral money to wallet
def add_referral_money(user, referral_code):
    # Updating Referred User Wallet
    referred_user = User.objects.get(referral_code=referral_code)
    if Wallet.objects.filter(user=referred_user).exists():
        referred_user_wallet = Wallet.objects.get(user=referred_user)
        referred_user_wallet.amount += 50
    else:
        referred_user_wallet = Wallet.objects.create(user=referred_user, amount=50)
    referred_user_wallet.save()
    transaction1 = WalletTransaction.objects.create(
        wallet=referred_user_wallet,
        description="Referral Offer",
        amount=50,
        is_credit=True,
    )
    transaction1.save()

    # Updating Current User Wallet
    current_user_wallet = Wallet.objects.create(user=user, amount=25)
    current_user_wallet.save()
    transaction2 = WalletTransaction.objects.create(
        wallet=current_user_wallet,
        description="Referral Offer",
        amount=25,
        is_credit=True,
    )
    transaction2.save()
