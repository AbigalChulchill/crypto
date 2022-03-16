# Required Libs For Binance Connnection
from binance import Client
import pandas as pd
import time

# Django Libs
from django.shortcuts import render


# Home Page
def home_page(request):
    return render(request, "pages/Home/index.html")



