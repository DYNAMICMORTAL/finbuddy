import random
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# API Configuration
INDIAN_STOCK_API_BASE = "https://stock.indianapi.in"
INDIAN_STOCK_API_KEY = "sk-live-HyFaz0NXK0RNIiShqwEgPMFdimnNrlVHfcOkxdJ2"

class MarketDataGenerator:
    """
    Enhanced market data generator with real API integration and fallback.
    Fetches real data from Indian Stock Exchange API, uses educational fallback when needed.
    """
    
    # Base prices for different symbols (educational reference points)
    BASE_PRICES = {
        'NIFTY': 19800,
        'BANKNIFTY': 44500,
        'SENSEX': 66000,
        'RELIANCE': 2450,
        'TCS': 3650,
        'HDFC': 1580,
        'INFY': 1420,
        'ICICIBANK': 950,
        'HDFCBANK': 1650,
        'WIPRO': 420,
        'BHARTIARTL': 880,
        'ITC': 410,
        'KOTAKBANK': 1780,
        'LT': 3200,
        'MARUTI': 10500
    }
    
    # Volatility factors (annual volatility as decimal)
    VOLATILITY = {
        'NIFTY': 0.15,
        'BANKNIFTY': 0.18,
        'SENSEX': 0.15,
        'RELIANCE': 0.25,
        'TCS': 0.22,
        'HDFC': 0.28,
        'INFY': 0.24,
        'ICICIBANK': 0.30,
        'HDFCBANK': 0.25,
        'WIPRO': 0.28,
        'BHARTIARTL': 0.26,
        'ITC': 0.20,
        'KOTAKBANK': 0.32,
        'LT': 0.24,
        'MARUTI': 0.26
    }

    def __init__(self):
        self.price_cache = {}
        self.last_update = {}
        # New: API data cache
        self.api_cache = {}
        self.api_cache_time = {}
        self.api_headers = {'X-Api-Key': INDIAN_STOCK_API_KEY}

    def _fetch_from_api(self, endpoint: str, params: dict = None) -> Optional[Dict]:
        """Fetch data from Indian Stock Exchange API with caching"""
        cache_key = f"{endpoint}_{str(params)}"
        current_time = time.time()
        
        # Return cached data if available and fresh (5 minutes)
        if cache_key in self.api_cache and (current_time - self.api_cache_time.get(cache_key, 0)) < 300:
            return self.api_cache[cache_key]
        
        try:
            url = f"{INDIAN_STOCK_API_BASE}{endpoint}"
            response = requests.get(url, headers=self.api_headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.api_cache[cache_key] = data
                self.api_cache_time[cache_key] = current_time
                return data
        except Exception as e:
            print(f"API fetch error for {endpoint}: {e}")
        
        return None

    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price with API integration"""
        # Try API first
        api_data = self._fetch_from_api("/stock", {"name": symbol})
        
        if api_data and isinstance(api_data, dict):
            # Extract price data from API response
            current_price = None
            change_percent = None
            
            # Handle different API response structures
            if 'current_price' in api_data:
                current_price = float(api_data['current_price'])
            elif 'price' in api_data:
                current_price = float(api_data['price'])
            elif 'ltp' in api_data:
                current_price = float(api_data['ltp'])
            
            if 'change_percent' in api_data:
                change_percent = float(api_data['change_percent'])
            elif 'chg_percent' in api_data:
                change_percent = float(api_data['chg_percent'])
            
            if current_price:
                return {
                    'symbol': symbol,
                    'price': round(current_price, 2),
                    'current_price': round(current_price, 2),
                    'ltp': round(current_price, 2),
                    'last_price': round(current_price, 2),
                    'change_percent': round(change_percent or 0, 2),
                    'chgPct': round(change_percent or 0, 2),
                    'change': round((current_price * (change_percent or 0) / 100), 2),
                    'volume': api_data.get('volume', random.randint(10000, 1000000)),
                    'high': api_data.get('high', round(current_price * 1.02, 2)),
                    'low': api_data.get('low', round(current_price * 0.98, 2)),
                    'open': api_data.get('open', round(current_price * (1 + random.gauss(0, 0.005)), 2)),
                    'prev_close': api_data.get('prev_close', round(current_price, 2)),
                    'data': {
                        'ltp': round(current_price, 2),
                        'price': round(current_price, 2),
                        'change_percent': round(change_percent or 0, 2)
                    },
                    'source': 'api'
                }
        
        # Fallback to educational data
        fallback_data = self._generate_fallback_price(symbol)
        fallback_data['source'] = 'educational_fallback'
        return fallback_data

    def _generate_fallback_price(self, symbol: str) -> Dict[str, Any]:
        """Generate fallback educational data"""
        base_price = self.BASE_PRICES.get(symbol, 1000)
        volatility = self.VOLATILITY.get(symbol, 0.25)
        
        # Add some randomness but keep it realistic
        current_time = time.time()
        if symbol not in self.last_update or (current_time - self.last_update[symbol]) > 300:  # 5 minutes
            # Generate new price with some drift
            if symbol in self.price_cache:
                last_price = self.price_cache[symbol]
                # Small random walk
                change_pct = random.gauss(0, volatility * 0.01)  # Daily vol / 100 for minute changes
                new_price = last_price * (1 + change_pct)
                # Keep within reasonable bounds (±20% from base)
                new_price = max(base_price * 0.8, min(base_price * 1.2, new_price))
            else:
                # Start near base price with small random variation
                new_price = base_price * (1 + random.gauss(0, 0.02))
            
            self.price_cache[symbol] = new_price
            self.last_update[symbol] = current_time
        
        current_price = self.price_cache[symbol]
        base_price = self.BASE_PRICES.get(symbol, current_price)
        
        # Calculate change percentage from base
        change_pct = ((current_price - base_price) / base_price) * 100
        
        return {
            'symbol': symbol,
            'price': round(current_price, 2),
            'current_price': round(current_price, 2),
            'ltp': round(current_price, 2),
            'last_price': round(current_price, 2),
            'change_percent': round(change_pct, 2),
            'chgPct': round(change_pct, 2),
            'change': round(current_price - base_price, 2),
            'volume': random.randint(10000, 1000000),
            'high': round(current_price * 1.02, 2),
            'low': round(current_price * 0.98, 2),
            'open': round(current_price * (1 + random.gauss(0, 0.005)), 2),
            'prev_close': round(base_price, 2),
            'data': {
                'ltp': round(current_price, 2),
                'price': round(current_price, 2),
                'change_percent': round(change_pct, 2)
            }
        }

    def get_trending_stocks(self) -> Dict[str, Any]:
        """Get trending stocks from API with fallback"""
        # Try API trending endpoint
        api_data = self._fetch_from_api("/trending")
        
        if api_data and isinstance(api_data, (list, dict)):
            trending_data = []
            stocks_data = api_data if isinstance(api_data, list) else api_data.get('data', [])
            
            for stock in stocks_data[:10]:  # Limit to top 10
                if isinstance(stock, dict):
                    symbol = stock.get('symbol', stock.get('name', ''))
                    if symbol:
                        trending_data.append({
                            'symbol': symbol,
                            'price': stock.get('price', stock.get('current_price', 0)),
                            'change_percent': stock.get('change_percent', stock.get('chg_percent', 0)),
                            'volume': stock.get('volume', 0)
                        })
            
            if trending_data:
                return {
                    'status': 'success',
                    'data': trending_data,
                    'trending_stocks': trending_data,
                    'source': 'api'
                }
        
        # Fallback to educational data
        trending_symbols = ['RELIANCE', 'TCS', 'HDFC', 'INFY', 'ICICIBANK']
        trending_data = []
        
        for symbol in trending_symbols:
            price_data = self._generate_fallback_price(symbol)
            trending_data.append({
                'symbol': symbol,
                'price': price_data['price'],
                'change_percent': price_data['change_percent'],
                'volume': price_data['volume']
            })
        
        return {
            'status': 'success',
            'data': trending_data,
            'trending_stocks': trending_data,
            'source': 'educational_fallback'
        }

    def generate_historical_data(self, symbol: str, period: str = '1d', num_candles: int = None) -> List[Dict]:
        """Generate historical data with API integration"""
        # Try API historical data
        period_map = {
            '1d': '1m', '1w': '1m', '1m': '1m', '3m': '6m', '1y': '1yr'
        }
        api_period = period_map.get(period, '1m')
        
        api_data = self._fetch_from_api("/historical_data", {
            "stock_name": symbol,
            "period": api_period,
            "filter": "default"
        })
        
        if api_data and isinstance(api_data, (list, dict)):
            historical_data = api_data if isinstance(api_data, list) else api_data.get('data', [])
            
            if historical_data:
                candles = []
                for item in historical_data:
                    if isinstance(item, dict):
                        # Handle different timestamp formats
                        timestamp = item.get('timestamp') or item.get('date') or item.get('time')
                        if timestamp:
                            if isinstance(timestamp, str):
                                try:
                                    timestamp = int(datetime.fromisoformat(timestamp.replace('Z', '+00:00')).timestamp())
                                except:
                                    timestamp = int(time.time())
                            
                            candle = {
                                'time': timestamp,
                                'timestamp': timestamp,
                                'date': datetime.fromtimestamp(timestamp).isoformat(),
                                'open': float(item.get('open', 0)),
                                'high': float(item.get('high', 0)),
                                'low': float(item.get('low', 0)),
                                'close': float(item.get('close', 0)),
                                'volume': int(item.get('volume', 0))
                            }
                            candles.append(candle)
                
                if candles:
                    return sorted(candles, key=lambda x: x['time'])
        
        # Fallback to educational data
        return self._generate_fallback_historical(symbol, period, num_candles)

    def _generate_fallback_historical(self, symbol: str, period: str = '1d', num_candles: int = None) -> List[Dict]:
        """Generate fallback historical data"""
        base_price = self.BASE_PRICES.get(symbol, 1000)
        volatility = self.VOLATILITY.get(symbol, 0.25)
        
        period_config = {
            '1d': {'candles': 78, 'interval_minutes': 5},
            '1w': {'candles': 35, 'interval_minutes': 60 * 3},
            '1m': {'candles': 30, 'interval_minutes': 60 * 24},
            '3m': {'candles': 90, 'interval_minutes': 60 * 24},
            '1y': {'candles': 52, 'interval_minutes': 60 * 24 * 7}
        }
        
        config = period_config.get(period, period_config['1d'])
        if num_candles:
            config['candles'] = num_candles
            
        candles = []
        current_price = base_price
        end_time = datetime.now()
        
        for i in range(config['candles']):
            candle_time = end_time - timedelta(minutes=config['interval_minutes'] * (config['candles'] - i - 1))
            timestamp = int(candle_time.timestamp())
            
            daily_vol = volatility / (252 ** 0.5)
            interval_vol = daily_vol * ((config['interval_minutes'] / (60 * 24)) ** 0.5)
            
            price_change_pct = random.gauss(0, interval_vol)
            new_price = current_price * (1 + price_change_pct)
            new_price = max(1, new_price)
            
            open_price = current_price
            close_price = new_price
            
            high_extra = random.uniform(0, 0.01) * abs(close_price - open_price) + random.uniform(0, 0.005) * open_price
            low_extra = random.uniform(0, 0.01) * abs(close_price - open_price) + random.uniform(0, 0.005) * open_price
            
            high_price = max(open_price, close_price) + high_extra
            low_price = min(open_price, close_price) - low_extra
            low_price = max(low_price, new_price * 0.95)
            
            candle = {
                'time': timestamp,
                'timestamp': timestamp,
                'date': candle_time.isoformat(),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': random.randint(1000, 100000)
            }
            
            candles.append(candle)
            current_price = new_price
        
        return candles

    def get_market_news(self) -> Dict[str, Any]:
        """Get market news from API with fallback"""
        api_data = self._fetch_from_api("/news")
        
        if api_data and isinstance(api_data, (list, dict)):
            news_data = api_data if isinstance(api_data, list) else api_data.get('data', [])
            
            if news_data:
                formatted_news = []
                for item in news_data[:10]:  # Limit to 10 items
                    if isinstance(item, dict):
                        formatted_news.append({
                            'title': item.get('title', item.get('headline', 'Market Update')),
                            'summary': item.get('summary', item.get('description', 'Market news update')),
                            'timestamp': item.get('timestamp', item.get('date', datetime.now().isoformat())),
                            'source': item.get('source', 'Indian Stock API')
                        })
                
                return {
                    'status': 'success',
                    'data': formatted_news,
                    'news': formatted_news,
                    'source': 'api'
                }
        
        # Fallback to sample news
        sample_news = [
            {
                'title': 'Market Update: Indices show mixed signals',
                'summary': 'Educational content: Markets demonstrate daily volatility patterns',
                'timestamp': datetime.now().isoformat(),
                'source': 'Educational Sample'
            },
            {
                'title': 'Sector Analysis: Technology stocks in focus',
                'summary': 'Learning module: Understanding sector rotation concepts',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'source': 'Educational Sample'
            }
        ]
        
        return {
            'status': 'success',
            'data': sample_news,
            'news': sample_news,
            'source': 'educational_fallback'
        }

# Global instance
market_data_generator = MarketDataGenerator()

def get_fallback_quote(symbol: str) -> Dict[str, Any]:
    """Get fallback quote data for a symbol"""
    return market_data_generator.get_current_price(symbol)

def get_fallback_historical(symbol: str, period: str = '1d') -> Dict[str, Any]:
    """Get fallback historical data for a symbol"""
    data = market_data_generator.generate_historical_data(symbol, period)
    return {
        'status': 'success',
        'data': data,
        'history': data,
        'prices': data
    }

def get_fallback_trending() -> Dict[str, Any]:
    """Get fallback trending stocks data"""
    return market_data_generator.get_trending_stocks()

# New: Bulk data fetcher for efficient API usage
def get_bulk_market_data(symbols: List[str]) -> Dict[str, Any]:
    """Fetch data for multiple symbols efficiently"""
    result = {
        'quotes': {},
        'trending': None,
        'news': None,
        'timestamp': time.time()
    }
    
    # Get quotes for all symbols
    for symbol in symbols:
        result['quotes'][symbol] = market_data_generator.get_current_price(symbol)
    
    # Get trending and news once
    result['trending'] = market_data_generator.get_trending_stocks()
    result['news'] = market_data_generator.get_market_news()
    
    return result
