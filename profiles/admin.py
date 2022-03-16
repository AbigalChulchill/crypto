from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(MarketCoins)
admin.site.register(TradingType)
admin.site.register(TradingStatus)
admin.site.register(TradingOrderType)
admin.site.register(ProfileDirectOrder)
admin.site.register(ProfileTrading)
admin.site.register(ProfileTradingOrders)
admin.site.register(AutomaticTradingCOinsMarketValues)
