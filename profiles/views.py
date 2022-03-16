# Required Libs For Binance Connnection
from binance.client import Client
import pandas as pd
import time
import asyncio, threading


# Django Libs
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

# Current app data
from .models import *
from .functions import *
from .forms import *

# User Trading Page Data
@login_required
def userTradingPage(request):


    # FORMS
    directMarketOrderForm = DirectMarketOrderForm()
    directLimitOrderForm = DirectLimitOrderForm()
    automaticTradingForm = AutomaticTradingForm()

    # Get the Current User
    profile = UserProfile.objects.filter(user= request.user).first()
    
    # User profile data
    user_first_name = request.user.first_name
    profile_image = None
    api_connection_status = None
    
    # Define coins list
    account_coins_list = list()
    first_coin = None

    # Check if profile found
    if profile:

        # Get Profile image
        profile_image = profile.profile_image

        # Connection Keys
        api_key = profile.api_key
        secret_key = profile.api_security_key

        # Get profile trades
        current_profile_running_trades = ProfileTrading.objects.filter(profile=profile).filter(trading_status = "0").order_by("-id")[0:5]
        current_profile_commplete_trades = ProfileTrading.objects.filter(profile=profile).filter(trading_status = "1").order_by("-id")[0:5]
        current_profile_direct_trades = ProfileDirectOrder.objects.filter(profile=profile).order_by("-id")[0:5]

        # API Connection Status
        api_connection_status = None

        try:

            # Ckeck api connection
            if api_key and secret_key:

                # Create Binance Client
                client = Client(api_key, secret_key)

                # Check client connection
                try:
                    # Check account status
                    client.get_account_status()

                    # API connection status [0 => Successfull Connected]
                    api_connection_status = 0

                    # Account Coins
                    account_info = client.get_account()

                    # Filter Coins
                    account_info_list = [filter_account_coins(info) for info in account_info["balances"]]
                    
                    # Filter available coins
                    for info in account_info_list:
                        if info != None:
                            account_coins_list.append(info)

                    # First Coin
                    first_coin = account_coins_list[0]

                except Exception as e:
                    print(e)
                    
                    # API connection status [1 => Invalid API Key or Security Key]
                    api_connection_status = 1
                    

            else:
                # API connection status [2 => No API Key Or Security Key detected]
                api_connection_status = 2
        
        except:

            # API connection status [3 => No Internet Connection]
            api_connection_status = 3
    
    else:

        # Create User Profile Form instance
        userProfileForm = UserProfileForm()
        
        # Create Profile
        return render(request, "pages/users/create_profile_first_time.html", {"form": userProfileForm})    
    

    # Returned Data
    context = {
        'user_first_name':user_first_name,
        'profile_image':profile_image,
        'api_connection_status':api_connection_status,
        'account_coins_list':account_coins_list,
        'first_coin': first_coin,
        'current_profile_running_trades':current_profile_running_trades,
        'current_profile_commplete_trades':current_profile_commplete_trades,
        'current_profile_direct_trades':current_profile_direct_trades,


        # Returned Forms
        "directMarketOrderForm":directMarketOrderForm,
        "directLimitOrderForm":directLimitOrderForm,
        "automaticTradingForm":automaticTradingForm,

    }

    return render(request, "pages/Profiles/profile_trading_page.html", context)

@login_required
def create_profile(request):
    if request.method == "POST":

        # Form
        form = UserProfileForm(request.POST, request.FILES)

        # Form Vlidation
        if form.is_valid():

            # Fitch the form data
            profile = form.save(commit=False)
            
            # Assign current user to profile
            profile.user = request.user

            # Save user profile
            profile.save()
        
    # Return to the trading view
    return redirect('User_Trading_Page')


@login_required
def display_user_profile(request):

    # Get the Current User
    profile = UserProfile.objects.filter(user= request.user).first()
    
    # User profile data
    user_first_name = request.user.first_name
    user_last_name = request.user.last_name
    user_email = request.user.email
    profile_image = None
    api_connection_status = None
    
    # Currnet User Password Form
    current_user_password_form = PasswordChangeForm(request.user)

    # Check if profile found
    if profile:

        # Get Profile image
        profile_image = profile.profile_image

        # Connection Keys
        api_key = profile.api_key
        secret_key = profile.api_security_key

        # API Connection Status
        api_connection_status = None

        try:

            # Ckeck api connection
            if api_key and secret_key:

                # Create Binance Client
                client = Client(api_key, secret_key)

                # Check client connection
                try:
                    # Check account status
                    client.get_account_status()

                    # API connection status [0 => Successfull Connected]
                    api_connection_status = 0

                except Exception as e:
                    print(e)
                    
                    # API connection status [1 => Invalid API Key or Security Key]
                    api_connection_status = 1
                    

            else:
                # API connection status [2 => No API Key Or Security Key detected]
                api_connection_status = 2
        
        except:

            # API connection status [3 => No Internet Connection]
            api_connection_status = 3
    
    else:

        # Create User Profile Form instance
        userProfileForm = UserProfileForm()
        
        # Create Profile
        return render(request, "pages/users/create_profile_first_time.html", {"form": userProfileForm})    
    

    # Returned Data
    context = {
        'user_first_name':user_first_name,
        'user_last_name':user_last_name,
        'user_email':user_email,
        'profile_image':profile_image,
        'api_connection_status':api_connection_status,

        # Forms
        "current_user_password_form": current_user_password_form,
    }

    return render(request, "pages/Profiles/profile.html", context)

@login_required
def update_user_data(request):
    if request.method == "POST":

        # Get the current user
        user = User.objects.get(id = request.user.id)
        
        # Get Request Data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('user_email')

        if first_name != "" and last_name != "" and email != "":

            # Update User Data
            user.first_name = first_name
            user.last_name = last_name
            user.email = email

            # Save User Data
            user.save()

    # Redirect User
    return redirect("display_user_profile")

@login_required
def update_profile_api(request):
    if request.method == "POST":

        # Get the current user
        profile = UserProfile.objects.get(user = request.user)
        
        # Get Request Data
        api_key = request.POST.get('binance_api_key')
        api_sec_key = request.POST.get('binance_api_security_key')

        # Check embity api
        if api_key != "" and api_sec_key != "":

            # Check api length
            if len(api_key) >= 60 and len(api_sec_key) >= 60:

                # Update User Data
                profile.api_key = api_key
                profile.api_security_key = api_sec_key

                # Save Profile Data
                profile.save()

    # Redirect User
    return redirect("display_user_profile")

@login_required
def update_profile_image(request):
    if request.method == "POST":

        # Get the current user
        profile = UserProfile.objects.get(user = request.user)
        
        # Catch Form
        form = UserProfileImageForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            # Save Profile Image    
            form.save()
        
        
    # Redirect User
    return redirect("display_user_profile")

@login_required
def change_current_user_password(request):
    if request.method == "POST":
        
        # Get current user password data
        current_user = PasswordChangeForm(request.user,request.POST)
        
        # Check Form Validation
        if current_user.is_valid():

            # Save New Password
            current_user.save()

            # Update Sessiob Hash
            update_session_auth_hash(request, current_user)


    # Redirect User
    return redirect("display_user_profile")


# ============================== Profile Trading =======================

# Get Coin Market Data
@login_required
def getCoinMarketData(request):
    if request.method == 'POST':
        if request.is_ajax():

            # Get the Current User
            profile = UserProfile.objects.filter(user= request.user).first()

            # Initializing the returned data
            data = dict()

            # Check if profile found
            if profile:

                # Connection Keys
                api_key = profile.api_key
                secret_key = profile.api_security_key

                try:
                    # Ckeck api connection
                    if api_key and secret_key:

                        # Create Binance Client
                        client = Client(api_key, secret_key)

                        # Check client connection
                        try:
                            # Check account status
                            client.get_account_status()
                            
                            # Valid Connection
                            data['API_STATUS'] = "TRUE"

                            # Get POST request Data
                            coin_name = request.POST.get('coin_name')
                            rate_hours = request.POST.get('rate_hours')

                            # Market Data 
                            market_data = getMarketData(api_key,secret_key,coin_name, "1m", int(rate_hours) * 60, 5)
                            

                            # GET Current ASSETS Balance
                            coin_1_name = coin_name.split('USDT')
                            coin_1_balance = client.get_asset_balance(asset=coin_1_name[0])
                            coin_2_balance = client.get_asset_balance(asset='USDT')

                            # Data Frame
                            data['DATA_FRAME'] = market_data
                            data['COINS'] = {
                                "coin_1_name": coin_1_name[0],
                                "coin_1": coin_1_balance["free"],
                                "coin_2": coin_2_balance["free"],
                            }

                            # Return Valid Connection 
                            return JsonResponse(data)

                        except Exception as e:
                            print(e)
                            data['API_STATUS'] = "FALSE"

                            # Invalid Key [=> Re Asssign the API Status]
                            return JsonResponse(data)
                    else:

                        data['API_STATUS'] = "FALSE"
                        # No API Key
                        return JsonResponse(data)
                except:

                    data['API_STATUS'] = "FALSE"
                    # No internet connection
                    return JsonResponse(data)


# Get Last 5 Running Trades
@login_required
def getLast5RunningTrades(request):
    if request.method == 'POST':
        if request.is_ajax():

            # Get the Current User
            profile = UserProfile.objects.filter(user= request.user).first()

            # Define Data dict
            data = dict()

            # Check if profile found
            if profile:

                # Get profile trades
                current_profile_trades = ProfileTrading.objects.filter(profile=profile).filter(trading_status = "0").order_by("-id")[0:5]

                # Trades list
                trades = list()

                # Loop Over the trades
                for trade in current_profile_trades:
                    temp = f'''
                                <tr>
                                    <td>{trade.first_trading_coin.coin_symbol}/{trade.second_trading_coin.coin_symbol}</td>
                                    <td>{trade.trading_type}</td>
                                    <td class="text-center">
                                        <ul class="table-controls">
                                            <li><a href="/profiles/automatic_trading/{trade.id}/" target="blank" data-toggle="tooltip" data-placement="top" title="Edit"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-eye"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg></a></li>
                                        </ul>
                                    </td>
                                </tr>
                            '''
                    
                    # Append Trading to trades list
                    trades.append(temp)

                # Set Profile Status
                data['PROFILE_STATUS'] = "TRUE"

                # Set Trades
                data['TRADES'] = trades

                # Return Trading Data
                return JsonResponse(data)
            
            else:

                # Set Profile Status
                data["PROFILE_STATUS"] = "FALSE"
            
            # Return No Profile Data
            return JsonResponse(data)

            
# Get Last 5 Complete Trades
@login_required
def getLast5CompleteTrades(request):
    if request.method == 'POST':
        if request.is_ajax():

            # Get the Current User
            profile = UserProfile.objects.filter(user= request.user).first()

            # Define Data dict
            data = dict()

            # Check if profile found
            if profile:

                # Get profile trades
                current_profile_trades = ProfileTrading.objects.filter(profile=profile).filter(trading_status = "1").order_by("-id")[0:5]

                # Trades list
                trades = list()

                # Loop Over the trades
                for trade in current_profile_trades:
                    temp = f'''
                                <tr>
                                    <td>{trade.first_trading_coin.coin_symbol}/{trade.second_trading_coin.coin_symbol}</td>
                                    <td>{trade.trading_type}</td>
                                    <td class="text-center">
                                        <ul class="table-controls">
                                            <li><a href="/profiles/automatic_trading/{trade.id}/" target="blank" data-toggle="tooltip" data-placement="top" title="Edit"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-eye"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg></a></li>
                                        </ul>
                                    </td>
                                </tr>
                            '''
                    
                    # Append Trading to trades list
                    trades.append(temp)

                # Set Profile Status
                data['PROFILE_STATUS'] = "TRUE"

                # Set Trades
                data['TRADES'] = trades

                # Return Trading Data
                return JsonResponse(data)
            
            else:

                # Set Profile Status
                data["PROFILE_STATUS"] = "FALSE"
            
            # Return No Profile Data
            return JsonResponse(data)

            
# Get Last 5 Direct Trades
@login_required
def getLast5DirectOrders(request):
    if request.method == 'POST':
        if request.is_ajax():

            # Get the Current User
            profile = UserProfile.objects.filter(user= request.user).first()

            # Define Data dict
            data = dict()

            # Check if profile found
            if profile:

                # Get profile trades
                current_profile_trades = ProfileDirectOrder.objects.filter(profile=profile).order_by("-id")[0:5]

                # Trades list
                trades = list()

                # Loop Over the trades
                for trade in current_profile_trades:
                    temp = f'''
                                <tr>
                                    <td>{trade.first_trading_coin.coin_symbol}/{trade.second_trading_coin.coin_symbol}</td>
                                    <td>{trade.trading_type}</td>
                                    <td>{trade.trading_order_type}</td>
                                    <td class="text-center">
                                        <ul class="table-controls">
                                            <li><a href="#"  data-toggle="tooltip" data-placement="top" title="Edit"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-eye"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg></a></li>
                                        </ul>
                                    </td>
                                </tr>
                            '''
                    
                    # Append Trading to trades list
                    trades.append(temp)

                # Set Profile Status
                data['PROFILE_STATUS'] = "TRUE"

                # Set Trades
                data['TRADES'] = trades

                # Return Trading Data
                return JsonResponse(data)
            
            else:

                # Set Profile Status
                data["PROFILE_STATUS"] = "FALSE"
            
            # Return No Profile Data
            return JsonResponse(data)
     


# -- FORMS -- [1] Direct Market Order
@login_required
def direct_market_order(request):
    if request.method == 'POST':
        if request.is_ajax():

            # Get the Current User
            profile = UserProfile.objects.filter(user= request.user).first()

            # Define Data dict
            data = dict()

            # Check if profile found
            if profile:

                # Set Profile Status
                data['PROFILE_STATUS'] = "TRUE"

                # Get Data
                first_trading_coin  = request.POST.get('first_trading_coin')
                second_trading_coin = request.POST.get('second_trading_coin')
                order_quantity      = request.POST.get('order_quantity')
                trading_order_type  = request.POST.get('trading_order_type')

                print('=' * 50)
                print(first_trading_coin)
                print(second_trading_coin)
                print(order_quantity)
                print(trading_order_type)
                print('=' * 50)

                # Get Coins data from database
                first_trading_coin_symbol = MarketCoins.objects.get(id = int(first_trading_coin))
                second_trading_coin_symbol = MarketCoins.objects.get(id = int(second_trading_coin))

                # Trading Order Type [SELL, BUY]
                trading_order_type = TradingOrderType.objects.get(id = int(trading_order_type))

                try:
                    
                    # [+] .----- Starting Trading LOGIC -----------
                    
                    # -- [1] Catch the Order Coins
                    coin_symbol = str(first_trading_coin_symbol.coin_symbol + second_trading_coin_symbol.coin_symbol)


                    # Connection Keys
                    api_key = profile.api_key
                    secret_key = profile.api_security_key


                    # Ckeck api connection
                    if api_key and secret_key:

                        # Create Binance Client
                        client = Client(api_key, secret_key)

                        # Check client connection and submit limit order
                        try:

                            # Check order Type
                            if trading_order_type.trading_order_type_symbol == "SELL":
                                
                                # Submit Sell Order
                                order = client.order_market_sell(symbol= coin_symbol, quantity=float(order_quantity))

                            elif trading_order_type.trading_order_type_symbol == "BUY":

                                # Submit Buy order
                                order = client.order_market_buy(symbol= coin_symbol, quantity=float(order_quantity))

                            else:

                                # Set Order Status to False
                                data["ORDER_STATUS"] = "FALSE"

                                # Return Trading Data
                                return JsonResponse(data) 


                        except Exception as e:
                            
                            # Set Order Status to False
                            data["ORDER_STATUS"] = "FALSE"

                            # Set Order Status to False
                            data["ORDER_ERROR_MESSAGE"] = str(e)

                            # Return Trading Data
                            return JsonResponse(data) 
                            

                    else:

                        # Set Profile Status
                        data["PROFILE_STATUS"] = "FALSE"

                        # Return Trading Data
                        return JsonResponse(data) 

                    # [+] .----- End Trading LOGIC -----------


                    # [+] Saving order in Darabase
                    if order:

                        print("-" * 50)
                        print(order)
                        print("-" * 50)
                        
                        # Set Trading Type To => MARKET
                        trading_type = TradingType.objects.get(trading_symbol = "MARKET")

                        # Trading Status
                        trading_status = TradingStatus.objects.get(trading_status_symbol = "NEW")

                        # Create Order Object
                        direct_market_order = ProfileDirectOrder.objects.create(
                                                                                profile= profile,
                                                                                first_trading_coin = first_trading_coin_symbol,
                                                                                second_trading_coin = second_trading_coin_symbol,
                                                                                order_quantity = str(order_quantity),
                                                                                limit_order_quantity = "0.0",
                                                                                trading_type = trading_type,
                                                                                trading_order_type = trading_order_type,
                                                                                trading_status = trading_status,
                                                                                ) 

                        # Saving Order
                        direct_market_order.save()             

                        # Set Order Status to True
                        data["ORDER_STATUS"] = "TRUE"

                except Exception as e:
                    
                    # Set Order Status to False
                    data["ORDER_STATUS"] = "FALSE"

                    # Set Order Status to False
                    data["ORDER_ERROR_MESSAGE"] = str(e)

                    # Return Trading Data
                    return JsonResponse(data)
                

                
                # Return Trading Data
                return JsonResponse(data)
            
            else:

                # Set Profile Status
                data["PROFILE_STATUS"] = "FALSE"


            # Return No Profile Data
            return JsonResponse(data)
     

# -- FORMS -- [2] Direct Limit Order
@login_required
def direct_limit_order(request):
    if request.method == 'POST':
        if request.is_ajax():

            # Get the Current User
            profile = UserProfile.objects.filter(user= request.user).first()

            # Define Data dict
            data = dict()

            # Check if profile found
            if profile:

                # Set Profile Status
                data['PROFILE_STATUS'] = "TRUE"

                # Get Data
                first_trading_coin      = request.POST.get('first_trading_coin')
                second_trading_coin     = request.POST.get('second_trading_coin')
                order_quantity          = request.POST.get('order_quantity')
                trading_order_type      = request.POST.get('trading_order_type')
                limit_price             = request.POST.get('limit_order_quantity')


                # Get Coins data from database
                first_trading_coin_symbol = MarketCoins.objects.get(id = int(first_trading_coin))
                second_trading_coin_symbol = MarketCoins.objects.get(id = int(second_trading_coin))

                # Trading Order Type [SELL, BUY]
                trading_order_type = TradingOrderType.objects.get(id = int(trading_order_type))

                try:
                    
                    # [+] .----- Starting Trading LOGIC -----------
                    
                    # -- [1] Catch the Order Coins
                    coin_symbol = str(first_trading_coin_symbol.coin_symbol + second_trading_coin_symbol.coin_symbol)


                    # Connection Keys
                    api_key = profile.api_key
                    secret_key = profile.api_security_key


                    # Ckeck api connection
                    if api_key and secret_key:

                        # Create Binance Client
                        client = Client(api_key, secret_key)

                        # Check client connection and submit limit order
                        try:

                            # Check order Type
                            if trading_order_type.trading_order_type_symbol == "SELL":
                                
                                # Submit Sell Order
                                order = client.order_limit_sell(symbol= coin_symbol, quantity=float(order_quantity) , price=str(limit_price))

                            elif trading_order_type.trading_order_type_symbol == "BUY":

                                # Submit Buy order
                                order = client.order_limit_buy(symbol= coin_symbol, quantity=float(order_quantity) , price=str(limit_price))

                            else:

                                # Set Order Status to False
                                data["ORDER_STATUS"] = "FALSE"

                                # Return Trading Data
                                return JsonResponse(data) 


                        except Exception as e:
                            
                            # Set Order Status to False
                            data["ORDER_STATUS"] = "FALSE"

                            # Set Order Status to False
                            data["ORDER_ERROR_MESSAGE"] = str(e)

                            # Return Trading Data
                            return JsonResponse(data) 
                            

                    else:

                        # Set Profile Status
                        data["PROFILE_STATUS"] = "FALSE"

                        # Return Trading Data
                        return JsonResponse(data) 


                    


                    # [+] .----- End Trading LOGIC -----------


                    # [+] Saving order in Darabase
                    if order['status'] == "NEW":
                        

                        # Set Trading Type To => MARKET
                        trading_type = TradingType.objects.get(trading_symbol = "LIMIT")

                        # Trading Status
                        trading_status = TradingStatus.objects.get(trading_status_symbol = "NEW")

                        # Create Order Object
                        direct_limit_order = ProfileDirectOrder.objects.create(
                                                                                profile= profile,
                                                                                first_trading_coin = first_trading_coin_symbol,
                                                                                second_trading_coin = second_trading_coin_symbol,
                                                                                order_quantity = str(order['origQty']),
                                                                                limit_order_quantity = str(order['price']),
                                                                                trading_type = trading_type,
                                                                                trading_order_type = trading_order_type,
                                                                                trading_status = trading_status,
                                                                                ) 

                        # Saving Order
                        direct_limit_order.save()             

                        # Set Order Status to True
                        data["ORDER_STATUS"] = "TRUE"
                    else:
                        # Set Profile Status
                        data["PROFILE_STATUS"] = "FALSE"

                        # Return No Profile Data
                        return JsonResponse(data)

                except Exception as e:
                    
                    # Set Order Status to False
                    data["ORDER_STATUS"] = "FALSE"

                    # Set Order Status to False
                    data["ORDER_ERROR_MESSAGE"] = str(e)

                    # Return Trading Data
                    return JsonResponse(data)
                

                
                # Return Trading Data
                return JsonResponse(data)
            
            else:

                # Set Profile Status
                data["PROFILE_STATUS"] = "FALSE"


            # Return No Profile Data
            return JsonResponse(data)


# -- FORMS -- [3] Automatic Trading
@login_required
def automatic_trading(request):
    if request.method == 'POST':
        if request.is_ajax():

            # Get the Current User
            profile = UserProfile.objects.filter(user= request.user).first()

            # Define Data dict
            data = dict()

            # Check if profile found
            if profile:

                # Set Profile Status
                data['PROFILE_STATUS'] = "TRUE"

                # Get Data
                first_trading_coin  = request.POST.get('first_trading_coin')
                second_trading_coin = request.POST.get('second_trading_coin')
                trading_quantity    = request.POST.get('trading_quantity')
                target_quantity     = request.POST.get('target_quantity')
                trading_type        = request.POST.get('trading_type')

                # Get Coins data from database
                first_trading_coin_symbol = MarketCoins.objects.get(id = int(first_trading_coin))
                second_trading_coin_symbol = MarketCoins.objects.get(id = int(second_trading_coin))

                # Trading Type [LIMIT, MARKET]
                trading_type = TradingType.objects.get(id = int(trading_type))

                try:
    
                    # Create Order Object
                    automatic_trading_order = ProfileTrading.objects.create(
                                                                            profile= profile,
                                                                            first_trading_coin = first_trading_coin_symbol,
                                                                            second_trading_coin = second_trading_coin_symbol,
                                                                            trading_quantity = str(trading_quantity),
                                                                            target_quantity = str(target_quantity),
                                                                            trading_type = trading_type,
                                                                            trading_status = "0"
                                                                            ) 

                    # Saving Order
                    automatic_trading_order.save()

                    # Connection Keys
                    api_key = profile.api_key
                    secret_key = profile.api_security_key


                    # Check asset account balance value
                    first_coin = account_coin_balance(api_key, secret_key, first_trading_coin_symbol.coin_symbol)
                    second_coin = account_coin_balance(api_key, secret_key, second_trading_coin_symbol.coin_symbol)


                    # Create Automatic Trading Market Value Opject
                    current_automatic_trading_coins_market_values = AutomaticTradingCOinsMarketValues.objects.create(
                                                                                                                    trading = automatic_trading_order,
                                                                                                                    first_coin_market_value = str(first_coin['free']),
                                                                                                                    second_coin_market_value = str(second_coin['free']),
                                                                                                                    )

                    # Save Trading Balance
                    current_automatic_trading_coins_market_values.save()

                    # Set Order Status to True
                    data["ORDER_STATUS"] = "TRUE"

                    # Run The current trading coins balance checker [Async Functions]
                    current_coins_balance_ckeckers = threading.Thread(target= asyncio.run, args=(coins_balance_ckeckers_async(api_key ,secret_key, automatic_trading_order.id), ))
                    current_coins_balance_ckeckers.start()

                    # Start trading process thread
                    trading_process = threading.Thread(target= asyncio.run, args=(limitBuyAndSellStrategy_async(api_key ,secret_key, automatic_trading_order.id), ))
                    trading_process.start()

                except Exception as e:
                    
                    # Set Order Status to False
                    data["ORDER_STATUS"] = "FALSE"

                    # Set Order Status to False
                    data["ORDER_ERROR_MESSAGE"] = str(e)

                    # Return Trading Data
                    return JsonResponse(data)
                
                
                
                # Return Trading Data
                return JsonResponse(data)
            
            else:

                # Set Profile Status
                data["PROFILE_STATUS"] = "FALSE"


            # Return No Profile Data
            return JsonResponse(data)




# =============================================================================
# -------------------- Automatic Trading Deals Pages --------------------------
@login_required
def automatic_trading_deal(request, id):
    # Get the Current User
    profile = UserProfile.objects.filter(user= request.user).first()
    
    # User profile data
    user_first_name = request.user.first_name
    profile_image = None
    api_connection_status = None
    
    context = dict()

    # Check if profile found
    if profile:

        # Get Profile image
        profile_image = profile.profile_image

        # Connection Keys
        api_key = profile.api_key
        secret_key = profile.api_security_key

        # API Connection Status
        api_connection_status = None

        try:

            # Ckeck api connection
            if api_key and secret_key:

                # Create Binance Client
                client = Client(api_key, secret_key)

                # Check client connection
                try:
                    # Check account status
                    client.get_account_status()

                    # API connection status [0 => Successfull Connected]
                    api_connection_status = 0


                    # =========================== START AUTOMATIC TRADING DATA ================
                    
                    # Catch the Trading Order
                    automatic_trading_order = ProfileTrading.objects.get(id = int(id))

                    # Check if trading order belongs to the current user
                    if automatic_trading_order.profile == profile:

                        # Get Order Data
                        first_coin = automatic_trading_order.first_trading_coin
                        second_coin = automatic_trading_order.second_trading_coin

                        # Get Tradig Transactions
                        trading_orders = ProfileTradingOrders.objects.filter(trading = automatic_trading_order)

                        # Get the current trading coins record
                        current_trading_coins_order = AutomaticTradingCOinsMarketValues.objects.filter(trading = automatic_trading_order).last()

                        # Returned Data
                        context['first_coin'] = first_coin
                        context['second_coin'] = second_coin
                        context['trading_orders'] = trading_orders
                        context['automatic_trading_order'] = automatic_trading_order.id
                        context['automatic_trading_order_status'] = automatic_trading_order.trading_status
                        context['current_trading_coins_order'] = current_trading_coins_order

                    else:

                        # Return current user to login page
                        return redirect("Login")



                    # =========================== END AUTOMATIC TRADING DATA ================


                except Exception as e:
                    print(e)
                    
                    # API connection status [1 => Invalid API Key or Security Key]
                    api_connection_status = 1
                    

            else:
                # API connection status [2 => No API Key Or Security Key detected]
                api_connection_status = 2
        
        except:

            # API connection status [3 => No Internet Connection]
            api_connection_status = 3
    
    else:

        # Create User Profile Form instance
        userProfileForm = UserProfileForm()
        
        # Create Profile
        return render(request, "pages/users/create_profile_first_time.html", {"form": userProfileForm})    
    

    # Returned Data
    context['user_first_name'] = user_first_name
    context['profile_image'] = profile_image
    context['api_connection_status'] = api_connection_status


    return render(request, "pages/Profiles/automatic_trading_page.html", context)


@login_required
def automatic_complete_trading_deal(request, id):
    # Get the Current User
    profile = UserProfile.objects.filter(user= request.user).first()
    
    # User profile data
    user_first_name = request.user.first_name
    profile_image = None
    api_connection_status = None
    
    context = dict()

    # Check if profile found
    if profile:

        # Get Profile image
        profile_image = profile.profile_image

        # Connection Keys
        api_key = profile.api_key
        secret_key = profile.api_security_key

        # API Connection Status
        api_connection_status = None

        try:

            # Ckeck api connection
            if api_key and secret_key:

                # Check client connection
                try:
                    

                    # API connection status [0 => Successfull Connected]
                    api_connection_status = 0


                    # =========================== START AUTOMATIC TRADING DATA ================
                    
                    # Catch the Trading Order
                    automatic_trading_order = ProfileTrading.objects.get(id = int(id))

                    # Check if trading order belongs to the current user
                    if automatic_trading_order.profile == profile:

                        # Get Order Data
                        first_coin = automatic_trading_order.first_trading_coin
                        second_coin = automatic_trading_order.second_trading_coin

                        # Get Tradig Transactions
                        trading_orders = ProfileTradingOrders.objects.filter(trading = automatic_trading_order)

                        # Get the current trading coins record
                        current_trading_coins_order = AutomaticTradingCOinsMarketValues.objects.filter(trading = automatic_trading_order).last()

                        # Returned Data
                        context['first_coin'] = first_coin
                        context['second_coin'] = second_coin
                        context['trading_orders'] = trading_orders
                        context['automatic_trading_order'] = automatic_trading_order.id
                        context['automatic_trading_order_status'] = automatic_trading_order.trading_status
                        context['current_trading_coins_order'] = current_trading_coins_order

                    else:

                        # Return current user to login page
                        return redirect("Login")



                    # =========================== END AUTOMATIC TRADING DATA ================


                except Exception as e:
                    print(e)
                    
                    # API connection status [1 => Invalid API Key or Security Key]
                    api_connection_status = 1
                    

            else:
                # API connection status [2 => No API Key Or Security Key detected]
                api_connection_status = 2
        
        except:

            # API connection status [3 => No Internet Connection]
            api_connection_status = 3
    
    else:

        # Create User Profile Form instance
        userProfileForm = UserProfileForm()
        
        # Create Profile
        return render(request, "pages/users/create_profile_first_time.html", {"form": userProfileForm})    
    

    # Returned Data
    context['user_first_name'] = user_first_name
    context['profile_image'] = profile_image
    context['api_connection_status'] = api_connection_status


    return render(request, "pages/Profiles/automatic_complete_trading_page.html", context)



@login_required
def getautomatictetradingdata(request):
    if request.method == 'POST':
        if request.is_ajax():
            

            # Get the Rquest data
            tradin_order_id = request.POST.get("id")

            # Get the Current User
            profile = UserProfile.objects.filter(user= request.user).first()

            # Catch the Trading Order
            automatic_trading_order = ProfileTrading.objects.get(id = int(tradin_order_id))

            # Define Data dict
            data = dict()

            # Check if trading order belongs to the current user
            if automatic_trading_order.profile == profile:

                # Get Tradig Transactions
                trading_orders = ProfileTradingOrders.objects.filter(trading = automatic_trading_order)

                # Get the current trading coins record
                current_trading_coins_market_data = AutomaticTradingCOinsMarketValues.objects.filter(trading = automatic_trading_order).last()


                # Trades list
                trades = list()

                # Loop Over the trades
                for trade in trading_orders:
                    temp = f'''
                                <tr>
                                    <td>{trade.id}</td>
                                    <td>{trade.first_trading_coin_quantity}</td>
                                    <td>{trade.second_trading_coin_quantity}</td>
                                    <td>{trade.trading_order_type.trading_order_type_symbol}</td>
                                </tr>
                            '''
                    
                    # Append Trading to trades list
                    trades.append(temp)

                data['TRADES'] = trades


                data['first_coin_market_value'] = current_trading_coins_market_data.first_coin_market_value,
                data['second_coin_market_value'] = current_trading_coins_market_data.second_coin_market_value,
                data['market_open'] = current_trading_coins_market_data.market_open,
                data['market_close'] = current_trading_coins_market_data.market_close,
                data['market_high'] = current_trading_coins_market_data.market_high,
                data['market_low'] = current_trading_coins_market_data.market_low,
        

                # Set Profile Status
                data['PROFILE_STATUS'] = "TRUE"

                # Return Trading Data
                return JsonResponse(data)
            
            else:

                # Set Profile Status
                data["PROFILE_STATUS"] = "FALSE"
            
            # Return No Profile Data
            return JsonResponse(data)


@login_required
def stoptradingorder(request):
    if request.method == 'POST':
        if request.is_ajax():
            

            # Get the Rquest data
            tradin_order_id = request.POST.get("id")

            # Get the Current User
            profile = UserProfile.objects.filter(user= request.user).first()

            # Catch the Trading Order
            automatic_trading_order = ProfileTrading.objects.get(id = int(tradin_order_id))

            # Define Data dict
            data = dict()

            # Check if trading order belongs to the current user
            if automatic_trading_order.profile == profile:

                # Stop Trading
                automatic_trading_order.trading_status = "3"

                # Save trading status
                automatic_trading_order.save()

                # Set Profile Status
                data['PROFILE_STATUS'] = "TRUE"

                # Return Trading Data
                return JsonResponse(data)
            
            else:

                # Set Profile Status
                data["PROFILE_STATUS"] = "FALSE"
            
            # Return No Profile Data
            return JsonResponse(data)


@login_required
def completetradingorder(request):
    if request.method == 'POST':
        if request.is_ajax():
            

            # Get the Rquest data
            tradin_order_id = request.POST.get("id")

            # Get the Current User
            profile = UserProfile.objects.filter(user= request.user).first()

            # Catch the Trading Order
            automatic_trading_order = ProfileTrading.objects.get(id = int(tradin_order_id))

            # Define Data dict
            data = dict()

            # Check if trading order belongs to the current user
            if automatic_trading_order.profile == profile:

                # Complete Trading
                automatic_trading_order.trading_status = "1"

                # Save trading status
                automatic_trading_order.save()

                # Set Profile Status
                data['PROFILE_STATUS'] = "TRUE"

                # Return Trading Data
                return JsonResponse(data)
            
            else:

                # Set Profile Status
                data["PROFILE_STATUS"] = "FALSE"
            
            # Return No Profile Data
            return JsonResponse(data)


@login_required
def reloadtradingorder(request):
    if request.method == 'POST':
        if request.is_ajax():
            

            # Get the Rquest data
            tradin_order_id = request.POST.get("id")

            # Get the Current User
            profile = UserProfile.objects.filter(user= request.user).first()

            # Catch the Trading Order
            automatic_trading_order = ProfileTrading.objects.get(id = int(tradin_order_id))

            # Define Data dict
            data = dict()

            # Check if trading order belongs to the current user
            if automatic_trading_order.profile == profile:


                
                # Complete Trading
                automatic_trading_order.trading_status = "1"

                # Save trading status
                automatic_trading_order.save()

                # Wait until Update task
                time.sleep(1)

                # Re-RUN Trading
                automatic_trading_order.trading_status = "0"

                # Save trading status
                automatic_trading_order.save()
                
                # ==================================================================
                # ---- Call Trading Functions
                
                # [1] API Connections
                # Connection Keys
                api_key = profile.api_key
                secret_key = profile.api_security_key

                
                # Run The current trading coins balance checker [Async Functions]
                current_coins_balance_ckeckers = threading.Thread(target= asyncio.run, args=(coins_balance_ckeckers_async(api_key ,secret_key, automatic_trading_order.id), ))
                current_coins_balance_ckeckers.start()

                # Start trading process thread
                trading_process = threading.Thread(target= asyncio.run, args=(limitBuyAndSellStrategy_async(api_key ,secret_key, automatic_trading_order.id), ))
                trading_process.start()
                # ==================================================================


                # Set Profile Status
                data['PROFILE_STATUS'] = "TRUE"

                # Return Trading Data
                return JsonResponse(data)
            
            else:

                # Set Profile Status
                data["PROFILE_STATUS"] = "FALSE"
            
            # Return No Profile Data
            return JsonResponse(data)

