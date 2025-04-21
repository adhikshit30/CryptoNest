from pycoingecko import CoinGeckoAPI
from .models import CoinPair

cg = CoinGeckoAPI()

def update_coin_prices():
    mapping = {
        'BTC/USDT': 'bitcoin',
        'ETH/USDT': 'ethereum',
        'XRP/USDT': 'ripple',
    }

    for symbol, gecko_id in mapping.items():
        try:
            price = cg.get_price(ids=gecko_id, vs_currencies='usd')[gecko_id]['usd']
            coin = CoinPair.objects.get(symbol=symbol)
            coin.current_price = price
            coin.save()
        except CoinPair.DoesNotExist:
            continue
        except Exception as e:
            print(f"Failed to update {symbol}: {e}")