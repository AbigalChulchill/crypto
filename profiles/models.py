from pyexpat import model
from django.db import models
from django.contrib.auth.models import User


# User Profiles Model
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', default="profile_images/default.png")
    api_key = models.CharField(max_length= 255)
    api_security_key = models.CharField(max_length= 255)


    def __str__(self):
        return self.user.username


# Market Coins
class MarketCoins(models.Model):
    coin_name = models.CharField(max_length= 100)
    coin_symbol = models.CharField(max_length= 10)
    coin_image = models.ImageField(upload_to='coin_images/', default="coin_images/default.png")
    trading_factor = models.CharField(max_length= 10, default="0.01")
    
    def __str__(self):
        return str(self.coin_name)


# Trading Type
class TradingType(models.Model):
    trading_name = models.CharField(max_length= 100)
    trading_symbol = models.CharField(max_length= 50)
    
    def __str__(self):
        return str(self.trading_name)


# Trading Status
class TradingStatus(models.Model):
    trading_status_name = models.CharField(max_length= 100)
    trading_status_symbol = models.CharField(max_length= 50)
    
    def __str__(self):
        return str(self.trading_status_name)

# Trading Status
class TradingOrderType(models.Model):
    trading_order_type_name = models.CharField(max_length= 100)
    trading_order_type_symbol = models.CharField(max_length= 50)
    
    def __str__(self):
        return str(self.trading_order_type_name)

# Profile Diret Orders
class ProfileDirectOrder(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    first_trading_coin = models.ForeignKey(MarketCoins, on_delete=models.CASCADE, related_name='first_trading_coin')
    second_trading_coin = models.ForeignKey(MarketCoins, on_delete=models.CASCADE, related_name='second_trading_coin')
    order_quantity = models.CharField(max_length= 100)
    limit_order_quantity = models.CharField(max_length= 100, default="0.0")
    trading_type = models.ForeignKey(TradingType, on_delete=models.CASCADE) 
    trading_order_type = models.ForeignKey(TradingOrderType, on_delete=models.CASCADE)
    trading_status = models.ForeignKey(TradingStatus, on_delete=models.CASCADE) 
    
    def __str__(self):
        return f"[{str(self.profile.user.username)}]-[{str(self.first_trading_coin.coin_symbol)}/{str(self.second_trading_coin.coin_symbol)}]" 

# Progile Automatic Tradings
class ProfileTrading(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    first_trading_coin = models.ForeignKey(MarketCoins, on_delete=models.CASCADE, related_name='first_profile_trading_coin')
    second_trading_coin = models.ForeignKey(MarketCoins, on_delete=models.CASCADE, related_name='second_profile_trading_coin')
    trading_quantity = models.CharField(max_length= 100)
    target_quantity = models.CharField(max_length= 100)
    trading_type = models.ForeignKey(TradingType, on_delete=models.CASCADE) 
    trading_status = models.CharField(max_length= 2, choices = (('0', 'RUN'),('1', 'COMPLETE'),('3', 'STOP'),), default=0)
    
    def __str__(self):
        return f"[{str(self.profile.user.username)}]-[{str(self.first_trading_coin.coin_symbol)}/{str(self.second_trading_coin.coin_symbol)}]" 

# Progile Automatic Tradings
class ProfileTradingOrders(models.Model):
    trading = models.ForeignKey(ProfileTrading, on_delete=models.CASCADE)
    first_trading_coin_quantity = models.CharField(max_length= 100)
    second_trading_coin_quantity = models.CharField(max_length= 100)
    trading_order_type = models.ForeignKey(TradingOrderType, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"[{str(self.trading.profile.user.username)}]-[{str(self.trading.first_trading_coin.coin_symbol)}/{str(self.trading.second_trading_coin.coin_symbol)}][{str(self.first_trading_coin_quantity)}/{str(self.second_trading_coin_quantity)}]" 


# Profile Automatic Trading Current trading coins market value
class AutomaticTradingCOinsMarketValues(models.Model):
    trading = models.ForeignKey(ProfileTrading, on_delete=models.CASCADE)
    first_coin_market_value = models.CharField(max_length= 100)
    second_coin_market_value = models.CharField(max_length= 100)
    market_open = models.CharField(max_length= 255, default= "0")
    market_close = models.CharField(max_length= 255, default= "0")
    market_high = models.CharField(max_length= 255, default= "0")
    market_low = models.CharField(max_length= 255, default= "0")

    def __str__(self) -> str:
        return f"[{self.trading.first_trading_coin.coin_symbol}/ {self.trading.second_trading_coin.coin_symbol}][{self.first_coin_market_value}/{self.second_coin_market_value}]"


