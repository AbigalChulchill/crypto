from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('create_profile/', views.create_profile, name="create_profile"),
    path('display_user_profile/', views.display_user_profile, name="display_user_profile"),
    path('update_user_data/', views.update_user_data, name="update_user_data"),
    path('update_profile_api/', views.update_profile_api, name="update_profile_api"),
    path('update_profile_image/', views.update_profile_image, name="update_profile_image"),
    path('change_current_user_password/', views.change_current_user_password, name="change_current_user_password"),

    # Profile Trading Data
    path('usertradingpage/', views.userTradingPage, name="User_Trading_Page"),
    path('getCoinMarketData/', views.getCoinMarketData, name="get_Coin_Market_Data"),

    # Get The Main Page Data
    path('getLast5RunningTrades/', views.getLast5RunningTrades, name="getLast5RunningTrades"),
    path('getLast5CompleteTrades/', views.getLast5CompleteTrades, name="getLast5CompleteTrades"),
    path('getLast5DirectOrders/', views.getLast5DirectOrders, name="getLast5DirectOrders"),
    
    # FORMS: [1] Direct Market Order
    path('direct_market_order/', views.direct_market_order, name="direct_market_order"),
    path('direct_limit_order/', views.direct_limit_order, name="direct_limit_order"),
    path('automatic_trading/', views.automatic_trading, name="automatic_trading"),

    # Automatic Trading
    path('automatic_trading/<id>/', views.automatic_trading_deal, name="automatic_trading_deal"),
    path('automatic_complete_trading_deal/<id>/', views.automatic_complete_trading_deal, name="automatic_complete_trading_deal"),
    
    path('getautomatictetradingdata/', views.getautomatictetradingdata, name="getautomatictetradingdata"),
    path('stoptradingorder/', views.stoptradingorder, name="stoptradingorder"),
    path('completetradingorder/', views.completetradingorder, name="completetradingorder"),
    path('reloadtradingorder/', views.reloadtradingorder, name="reloadtradingorder"),
    
]