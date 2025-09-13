# utils.py
from decimal import Decimal
from ...models import Commission

def get_commission():
    try:
        commission = Commission.objects.first()
        return commission.valeur
    except Exception as e:
        return Decimal("2.00")
