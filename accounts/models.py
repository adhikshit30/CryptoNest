from django.db import models
from django.contrib.auth.models import User



# Create your models here.

# 1. Simulated coin pairs
class CoinPair(models.Model):
    symbol = models.CharField(max_length=10)  # e.g., BTC/USDT
    current_price = models.FloatField(default=0.0)

    def __str__(self):
        return self.symbol

# 2. User's portfolio (holdings per coin)
class UserPortfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.ForeignKey(CoinPair, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.coin.symbol}"

# 3. Simulated trade order
class TradeOrder(models.Model):
    ORDER_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin = models.ForeignKey(CoinPair, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=4, choices=ORDER_TYPES)
    quantity = models.FloatField()
    price_at_order = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.order_type.upper()} {self.coin.symbol} {self.quantity} @ {self.price_at_order}"