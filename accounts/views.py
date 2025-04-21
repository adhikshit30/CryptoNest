from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.http import HttpResponse
from .models import CoinPair
from django.contrib import messages
from .models import CoinPair, TradeOrder, UserPortfolio

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import TradeOrder
from .price_updater import update_coin_prices
from pycoingecko import CoinGeckoAPI
import numpy as np
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db.models import Avg


# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

def home_view(request):
    return render(request, 'accounts/home.html')

@login_required
def dashboard_view(request):
    update_coin_prices()  # ⬅ fetch live prices before showing
    coins = CoinPair.objects.all()
    return render(request, 'accounts/dashboard.html', {'coins': coins})

@csrf_protect
@login_required
def place_order_view(request):
    if request.method == 'POST':
        order_type = request.POST.get('order_type')
        coin_id = request.POST.get('coin_id')
        try:
            quantity = float(request.POST.get('quantity'))
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity.")
            return redirect('dashboard')

        if quantity <= 0:
            messages.error(request, "Quantity must be greater than zero.")
            return redirect('dashboard')

        try:
            coin = CoinPair.objects.get(id=coin_id)
        except CoinPair.DoesNotExist:
            messages.error(request, "Invalid coin pair.")
            return redirect('dashboard')

        user = request.user
        price = coin.current_price

        portfolio, created = UserPortfolio.objects.get_or_create(user=user, coin=coin)

        # ✅ Validation for sell
        if order_type == 'sell':
            if portfolio.quantity < quantity:
                messages.error(request, "Insufficient balance to sell.")
                return redirect('dashboard')
            else:
                portfolio.quantity -= quantity

        # ✅ For buy, just add to quantity
        elif order_type == 'buy':
            portfolio.quantity += quantity

        # Save changes
        portfolio.save()

        TradeOrder.objects.create(
            user=user,
            coin=coin,
            order_type=order_type,
            quantity=quantity,
            price_at_order=price,
        )

        messages.success(request, f"{order_type.capitalize()} order placed for {quantity} {coin.symbol}!")
        return redirect('dashboard')
    

@login_required
def portfolio_view(request):
    holdings = UserPortfolio.objects.filter(user=request.user)

    labels = [h.coin.symbol for h in holdings]
    quantities = [float(h.quantity) for h in holdings]

    # CoinGecko setup (already there)
    cg = CoinGeckoAPI()

    coin_mapping = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'XRP': 'ripple',
    }

    price_trends = {}
    total_value = 0  # 💰 initialize total

    total_trades = TradeOrder.objects.filter(user=request.user).count()

    # 🧮 Avg price per coin (buy orders only)
    avg_prices = (
        TradeOrder.objects
        .filter(user=request.user, order_type='buy')
        .values('coin__symbol')
        .annotate(avg_price=Avg('price_at_order'))
    )

    avg_price_dict = {item['coin__symbol']: round(item['avg_price'], 2) for item in avg_prices}

    # 🧮 Coin with highest holdings
    if holdings:
        top_coin = max(holdings, key=lambda h: h.quantity)
        top_coin_name = top_coin.coin.symbol
    else:
        top_coin_name = "N/A"

    for symbol, gecko_id in coin_mapping.items():
        try:
            raw_data = cg.get_coin_market_chart_by_id(id=gecko_id, vs_currency='usd', days=7)
            prices = [p[1] for p in raw_data['prices']]
            sampled_prices = np.linspace(0, len(prices) - 1, 7, dtype=int)
            price_trends[symbol] = [round(prices[i], 2) for i in sampled_prices]

            # ✅ Calculate total for this coin if user owns it
            for h in holdings:
                if h.coin.symbol.startswith(symbol):
                    total_value += h.quantity * prices[-1]  # most recent price
        except:
            price_trends[symbol] = [0] * 7

    total_value = round(total_value, 2)  # round off nicely

    return render(request, 'accounts/portfolio.html', {
        'holdings': holdings,
        'labels': labels,
        'quantities': quantities,
        'price_trends': price_trends,
        'total_value': total_value,
        'total_trades': total_trades,
        'avg_price_dict': avg_price_dict,
        'top_coin_name': top_coin_name,
    })

    

@login_required
def trade_history_view(request):
    trades = TradeOrder.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'accounts/trade_history.html', {'trades': trades})

