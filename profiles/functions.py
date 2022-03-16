# Required Libs
from binance.client import Client
import pandas as pd
import time
import datetime as dt
import asyncio, threading

from profiles.models import *

# ----------- Django Libs
from asgiref.sync import sync_to_async

# -- Functions ----

def getMarketData(api_key, secret_key,currency, interval, lookback, data_step):
    """
        [+] Function name: Get Market Data
        [+] Function Parameter:
                [1] API_Key : API Key for Stablishing connection
                [2] API_Security_Key: For Authorize the conniction
                [3] Currency: Reuired Market Data For Specific Currency ex: [BTCUSDT]
                [4] Interval: Reuired Loading Interval Default: 1 min
                [5] Lookback: Collecting Range
                [6] Data_Step: Step number for cutting data
    """


    # Create Binance Client
    client = Client(api_key, secret_key)

    # Loop Until Catch the Market Data
    while True:
        try:
            # Get Market Data
            frame = pd.DataFrame(client.get_historical_klines(currency, interval, str(lookback) + ' min ago UTC'))
            
            # Wait unti data comming
            time.sleep(2)
            
            # Check if data still empty
            if frame.empty:
                continue
            
            # End Loop if frame not empty
            break
        except Exception as e:
            print("=" * 50)
            print("[*] Exception From Getting Market Data Funcion: ", e)
            print("=" * 50)

            # Continue in loop
            continue
    
    # Rename Frame cols
    frame.columns = ['Time','Open','High','Low','Close','Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    
    # Set time is the index
    frame = frame.set_index('Time')
    
    # Convert frame time to the default time
    frame.index = pd.to_datetime(frame.index,unit='ms')
    
    # Open Market Data
    open_market_data = frame.Open.tolist()

    # Close Market Data
    close_market_data = frame.Close.tolist()

    # High Market Data
    high_market_data = frame.High.tolist()

    # Low Market Data
    low_market_data = frame.Low.tolist()

    # Market Time
    market_time = [dt.datetime.time(d) for d in frame.index] 

    data = {
        "Open": open_market_data[0:-1:data_step],
        "Close": close_market_data[0:-1:data_step],
        "High": high_market_data[0:-1:data_step],
        "Low": low_market_data[0:-1:data_step],
        "Time": market_time[0:-1:data_step],
    }

    # Return frame
    return data


def filter_account_coins(info):
    """
        [+] Function name: filter account coins
        [+] Function Parameter:
                [1] Info : Account Coins info
    """

    if info["free"] not in ["0.00000000", "0.00", "0.0", "0", "0.000"] and info["free"] not in ["0.00000000", "0.00", "0.0", "0", "0.000"]:
        if info["asset"] not in ["USDT"]:
            return info


def account_coin_balance(api_key, api_security_key, coin):
    
    """
        [+] Function name: filter account coins
        [+] Function Parameter:
                [1] API_Key : API Key for Stablishing connection
                [2] API_Security_Key: For Authorize the conniction
                [3] Coin: reuored coin
    """
    
    # Create Binance Client
    client = Client(api_key, api_security_key)

    # Loop Until Catch the Market Data
    while True:
        # Get Market Data
        frame = client.get_asset_balance(asset=str(coin))
        
        # Check if data still empty
        if not frame:
            # Wait unti data comming
            time.sleep(2)

            # Rebeat Loop
            continue
        
        # End Loop if frame not empty
        context = {
            'free': frame["free"]
        }

        # Return frame
        return context


# Balance Checker Async Function
async def coins_balance_ckeckers_async(api_key ,secret_key, tradingOrderID):

    """
        [+] Function name: coins balance ckeckers [Sync Function]
        [+] Function Parameter:
                [1] API_Key : API Key for Stablishing connection
                [2] API_Security_Key: For Authorize the conniction
                [3] Trading Order ID: CUrrent Automatic Trading Order ID
        [+] Description:
                This function is a [Aync] function called from a [Thread] process to check and update
                the current trading order coins values and also update the current coins market data.
    """

    # Call The Coin balance checkers [Sync function]
    sync_to_async(coins_balance_ckeckers(api_key ,secret_key, tradingOrderID), thread_sensitive=True)



# Balance Checker Sync Function
def coins_balance_ckeckers(api_key ,secret_key, tradingOrderID):
    
    """
        [+] Function name: coins balance ckeckers [Sync Function]
        [+] Function Parameter:
                [1] API_Key : API Key for Stablishing connection
                [2] API_Security_Key: For Authorize the conniction
                [3] Trading Order ID: CUrrent Automatic Trading Order ID
        [+] Description:
                This function is a [Sync] function called from an [Async] function to check and update
                the current trading order coins values and also update the current coins market data.
    """


    # Get the trading order
    trading_order = ProfileTrading.objects.get(id = int(tradingOrderID))

    # CHeck if the order is exists or not
    if trading_order:

        # Current trading coins
        first_trading_coin_symbol = str(trading_order.first_trading_coin.coin_symbol)
        second_trading_coin_symbol = str(trading_order.second_trading_coin.coin_symbol)

        # Current trading coins
        current_trading_coins = str(first_trading_coin_symbol + second_trading_coin_symbol)

    else:

        # Return When no order
        return


    # Get the current trading coins record
    current_trading_coins_order = AutomaticTradingCOinsMarketValues.objects.filter(trading = trading_order).last()

    # Update Loop
    while True:

        # Get the trading order data
        trading_order = ProfileTrading.objects.get(id = int(tradingOrderID))

        # Check the trading order status
        if trading_order.trading_status == "0": # RUN STATE
            
            # Check the coins balacnce
            first_coin = account_coin_balance(api_key, secret_key, first_trading_coin_symbol)
            second_coin = account_coin_balance(api_key, secret_key, second_trading_coin_symbol)

            # Update Current Trading  Coins Database
            current_trading_coins_order.first_coin_market_value = first_coin["free"]
            current_trading_coins_order.second_coin_market_value = second_coin["free"]

            # Update account balance
            current_trading_coins_order.save()

            # Update market data [open, close, high, low]
            current_coins_market_data = getMarketData(api_key, secret_key, current_trading_coins, "1m", "2", 1)

            # Update Current Trading  Coins Database
            current_trading_coins_order.market_open = current_coins_market_data["Open"][0]
            current_trading_coins_order.market_close = current_coins_market_data["Close"][0]
            current_trading_coins_order.market_high = current_coins_market_data["High"][0]
            current_trading_coins_order.market_low = current_coins_market_data["Low"][0]

            # Update account Trading  Coins Database
            current_trading_coins_order.save()

            # wait until next update
            time.sleep(5)

        else: # STOP or Complete STATE

            # End Async function
            return



# Trading Strategy [Automatic limit trading ][ASync]
async def limitBuyAndSellStrategy_async(api_key ,secret_key, tradingOrderID):
    
    """
        [+] Function name: Limit Buy And Sell Strategy [ASync Function]
        [+] Function Parameter:
                [1] API_Key : API Key for Stablishing connection
                [2] API_Security_Key: For Authorize the conniction
                [3] Trading Order ID: CUrrent Automatic Trading Order ID
        [+] Description:
                This function is a [Sync] function called from an [Async] function to check and update
                the current trading order coins values and also update the current coins market data.
    """

    # Call The Coin balance checkers [ASync function]
    sync_to_async(limitBuyAndSellStrategy(api_key ,secret_key, tradingOrderID), thread_sensitive=True)



# Trading Strategy [Automatic limit trading ][Sync]
def limitBuyAndSellStrategy(api_key ,secret_key, tradingOrderID):
    
    """
        [+] Function name: Limit Buy And Sell Strategy [Sync Function]
        [+] Function Parameter:
                [1] API_Key : API Key for Stablishing connection
                [2] API_Security_Key: For Authorize the conniction
                [3] Trading Order ID: CUrrent Automatic Trading Order ID
        [+] Description:
                This function is a [Sync] function called from an [Async] function to check and update
                the current trading order coins values and also update the current coins market data.
    """

    # Get the trading order
    trading_order = ProfileTrading.objects.get(id = int(tradingOrderID))

    # CHeck if the order is exists or not
    if trading_order:

        # Current trading coins
        first_trading_coin_symbol = str(trading_order.first_trading_coin.coin_symbol)
        second_trading_coin_symbol = str(trading_order.second_trading_coin.coin_symbol)

        # First Coin Trading Factor
        first_coin_trading_factor = float(trading_order.first_trading_coin.trading_factor)

        # Current trading coins
        current_trading_coins = str(first_trading_coin_symbol + second_trading_coin_symbol)

    else:

        # Return When no order
        return
    
    # Create Binance Client
    client = Client(api_key, secret_key)

    
    # Global values for first time
    trading_quantity = float(trading_order.trading_quantity)
    last_buy_value = 0
    last_sell_value = 0
    errors = 0
    
    # Loop until get the trading
    while True:
        
        try:
            # Get Current Symbol trading list
            trades = pd.DataFrame(client.get_my_trades(symbol=current_trading_coins))
            
            # Wait 2 seconds
            time.sleep(2)
            
            # Check the trading dataframe
            if trades.empty:
                print("-" * 50)
                print("- [*] Error: last trading history is empty - ")
                print("-" * 50)

                # Reloop
                continue

        except Exception as e:

            print("-" * 50)
            print("- [*] Error: Could not reading last trading history - Pleace check internet connection ...")
            print(f"- [*] Error: {e}")
            
            
            # Trading Stoped 
            trading_order.trading_status = "3"
            
            # Save the trading order status
            trading_order.save()
            
            # Stop trading Message
            print(f"[-] OrderID: {trading_order.id} STOPPED! - ")
            print("-" * 50)

            # Stop trading
            return
            

        # Exit Loop after finding the last trading list
        break
    
    # Get the Last trade
    last_trade = trades.iloc[-1]

    # Check the last trading action type
    if last_trade.isBuyer:

        # Update last trading price
        last_buy_value = float(last_trade.price)

        # Enable Sell
        entried = True
    else:

        # Update last trading price
        last_sell_value = float(last_trade.price)

        # Enable Buy
        entried = False
    
    
    # Trading Loop [Buy and Sell]
    while True:
        
        # Get the trading order data
        trading_order = ProfileTrading.objects.get(id = int(tradingOrderID))

        # Check the trading order status
        if trading_order.trading_status == "1" or trading_order.trading_status == "3": # COMPLETE STATE OR STOP STATE
             
            print("-" * 50)
            print(f"[+] Trading Complete Successsfull")
            print("-" * 50)

            # Break the Loop [Target Matched]
            return
            
        else:
            try:
                
                # Buy state
                if not entried:
                    
                    # Get the market closing data
                    current_order_market_values = AutomaticTradingCOinsMarketValues.objects.get(trading = trading_order)
                    
                    # Get Low Buy Value
                    close_value = current_order_market_values.market_close
                    
                    # Close Value For Condition
                    float_close_value = float(close_value)
                    
                    # Start Buy
                    if float_close_value < last_sell_value:
                    
                        # Get the second coin balance
                        current_second_currency_value = float(current_order_market_values.second_coin_market_value)
                        
                        # Check the Buy balance state [this will repeat until the sell order done]
                        if current_second_currency_value <= trading_quantity:
                            
                            print(f"[+] currient {second_trading_coin_symbol} quantity is not enugh, current_{second_trading_coin_symbol}_currency= {current_second_currency_value}| trading_buy_quantity= {trading_quantity}")

                            # Loop again
                            continue

                        
                        # Clac the buy factor
                        buy_factor = float(current_order_market_values.market_low) * float(first_coin_trading_factor)
                        
                        # Listing Price For Buy
                        Market_Low_Value = float(float(current_order_market_values.market_low) - buy_factor)
                        
                        # Calculate the trading ammont
                        trading_buy_value = float(trading_quantity / Market_Low_Value)
                        
                        # Buy Action
                        while True:
                            try:
                                    
                                # Try to set the order
                                order = client.order_limit_buy(symbol=current_trading_coins, quantity=float(trading_buy_value), price=str(Market_Low_Value))

                                # Check the order status
                                if order['status'] == "NEW":
                                    
                                    # Save Buy order
                                    buy_order = ProfileTradingOrders.objects.create(

                                        trading = trading_order,
                                        first_trading_coin_quantity = str(trading_buy_value),
                                        second_trading_coin_quantity = str(trading_quantity),
                                        trading_order_type = TradingOrderType.objects.filter(trading_order_type_symbol = "BUY").first(),
                                    )

                                    # Save Buy order to DB
                                    buy_order.save()

                                    # Order Setted Successfully
                                    break

                            except Exception as e:

                                print("-" * 50)
                                print(f"Exception While Sending Buy Order: {e}")
                                print("-" * 50)

                                # Try again to set an order
                                continue

                        # Buy Prise
                        last_buy_value = float(order['fills'][0]['price'])
                        
                        # Order ID
                        order_id = order['orderID']

                        # Check the order status
                        while True:
                            try:

                                # Send Check request
                                check_order = client.get_order( symbol=current_trading_coins, orderId=order_id)
                                
                                # Check if order 
                                if check_order["status"] == 'FILLED':

                                    # Break the loop
                                    break
                                
                                # Wait until the next check
                                time.sleep(5)

                            except Exception as e:
                                print(f"Exception From Buy Method: {e}")

                                # Complete the loop
                                continue

                        # Reset the entried value
                        entried = True     

                else:
                    # -- Sell State
                    print("-" * 50)
                    print(f"[+] Try to sell")
                    print("-" * 50)


                    # Get the market closing data
                    current_order_market_values = AutomaticTradingCOinsMarketValues.objects.get(trading = trading_order)
                    
                    # Get Low Buy Value
                    Open_value = current_order_market_values.market_open
                    
                    # Open value for condition
                    float_open_value = float(Open_value)
                    
                    # Sell Condition
                    if float_open_value > last_buy_value:
                        
                        # Get the second coin balance
                        current_first_currency_value = float(current_order_market_values.first_coin_market_value)
                        
                        # Calculating trading sell quantity
                        trading_sell_quantity = float(trading_quantity / last_buy_value)
                        
                        # Check the Sell balance state [This state be repeated until the buy action done]
                        if current_first_currency_value < trading_sell_quantity:
                            print(f"[+] currient {first_trading_coin_symbol} quantity is not enugh, current_{first_trading_coin_symbol}_currency= {current_first_currency_value}| trading_sell_quantity= {current_first_currency_value}")
                            # Loop Again
                            continue
                        
                        # Clac the Sell factor
                        sell_factor = float(current_order_market_values.market_high) * float(first_coin_trading_factor)
                        
                        # Listing Price For Sell
                        Market_High_Value = float(float(current_order_market_values.market_high) + sell_factor)

                        # Sell Action
                        while True:
                            try:
                                    
                                # Try to set the order
                                order = client.order_limit_sell(symbol=current_trading_coins, quantity=float(current_first_currency_value), price=str(Market_High_Value))

                                # Check the order status
                                if order['status'] == "NEW":
                                    
                                    # Save Sell order
                                    sell_order = ProfileTradingOrders.objects.create(

                                        trading = trading_order,
                                        first_trading_coin_quantity = current_first_currency_value,
                                        second_trading_coin_quantity = str(float(current_first_currency_value) * float(Market_High_Value)),
                                        trading_order_type = TradingOrderType.objects.filter(trading_order_type_symbol = "SELL").first(),
                                    )

                                    # Save Sell order to DB
                                    sell_order.save()

                                    # Order Setted Successfully
                                    break

                            except Exception as e:

                                print("-" * 50)
                                print(f"Exception While Sending Sell Order: {e}")
                                print("-" * 50)

                                # Try again to set an order
                                continue

                        # Sell Price
                        last_sell_value = float(order['fills'][0]['price'])

                        # Order ID
                        order_id = order['orderID']

                        # Check the order status
                        while True:
                            try:

                                # Send Check request
                                check_order = client.get_order( symbol=current_trading_coins, orderId=order_id)
                                
                                # Check if order 
                                if check_order["status"] == 'FILLED':

                                    # Break the loop
                                    break
                                
                                # Wait until the next check
                                time.sleep(5)

                            except Exception as e:
                                print(f"Exception From Sell Method: {e}")

                                # Complete the loop
                                continue

                        # Reset the entried value
                        entried = False
                    
            except:
                errors += 1
                print(f'[*] Error Happen! ... Error No: {errors} at {time.ctime()}')
                continue

    
    return 

