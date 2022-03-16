from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

from .models import *


# Profile Form
class UserProfileForm(ModelForm):

    class Meta:
        model = UserProfile
        fields = [
            "profile_image",
            "api_key",
            "api_security_key",
        ]


    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        # Field Classes
        self.fields['profile_image'].widget.attrs['class'] = 'form-control'
        
        self.fields['api_key'].widget.attrs['class'] = 'form-control'
        self.fields['api_key'].widget.attrs['placeholder'] = 'Binance API Key'

        self.fields['api_security_key'].widget.attrs['class'] = 'form-control'
        self.fields['api_security_key'].widget.attrs['placeholder'] = 'Binance API Security Key'

# Profile Image Form
class UserProfileImageForm(ModelForm):

    class Meta:
        model = UserProfile
        fields = [
            "profile_image"
        ]


    def __init__(self, *args, **kwargs):
        super(UserProfileImageForm, self).__init__(*args, **kwargs)

        # Field Classes
        self.fields['profile_image'].widget.attrs['class'] = 'form-control'




# Direct MARKET ORDER
class DirectMarketOrderForm(ModelForm):

    class Meta:
        model = ProfileDirectOrder
        fields = [
            "first_trading_coin",
            "second_trading_coin",
            "order_quantity",
            "trading_order_type",
        ]


    def __init__(self, *args, **kwargs):
        super(DirectMarketOrderForm, self).__init__(*args, **kwargs)

        # Field Classes
        self.fields['first_trading_coin'].widget.attrs['class'] = 'form-control'
        self.fields['second_trading_coin'].widget.attrs['class'] = 'form-control'
        self.fields['order_quantity'].widget.attrs['class'] = 'form-control'
        self.fields['trading_order_type'].widget.attrs['class'] = 'form-control'
        

# Direct LIMIT ORDER
class DirectLimitOrderForm(ModelForm):

    class Meta:
        model = ProfileDirectOrder
        fields = [
            "first_trading_coin",
            "second_trading_coin",
            "order_quantity",
            "limit_order_quantity",
            "trading_order_type",
        ]


    def __init__(self, *args, **kwargs):
        super(DirectLimitOrderForm, self).__init__(*args, **kwargs)

        # Field Classes
        self.fields['first_trading_coin'].widget.attrs['class'] = 'form-control'
        self.fields['second_trading_coin'].widget.attrs['class'] = 'form-control'
        self.fields['order_quantity'].widget.attrs['class'] = 'form-control'
        self.fields['limit_order_quantity'].widget.attrs['class'] = 'form-control'
        self.fields['trading_order_type'].widget.attrs['class'] = 'form-control'



# Automatic Trading
class AutomaticTradingForm(ModelForm):

    class Meta:
        model = ProfileTrading
        fields = [
            "first_trading_coin",
            "second_trading_coin",
            "trading_quantity",
            "target_quantity",
            "trading_type",
        ]


    def __init__(self, *args, **kwargs):
        super(AutomaticTradingForm, self).__init__(*args, **kwargs)

        # Field Classes
        self.fields['first_trading_coin'].widget.attrs['class'] = 'form-control'
        self.fields['second_trading_coin'].widget.attrs['class'] = 'form-control'
        self.fields['trading_quantity'].widget.attrs['class'] = 'form-control'
        self.fields['target_quantity'].widget.attrs['class'] = 'form-control'
        self.fields['trading_type'].widget.attrs['class'] = 'form-control'

