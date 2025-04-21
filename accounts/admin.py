from django.contrib import admin
from .models import CoinPair, TradeOrder, UserPortfolio

# Register your models here.
admin.site.register(CoinPair)
admin.site.register(TradeOrder)
admin.site.register(UserPortfolio)
