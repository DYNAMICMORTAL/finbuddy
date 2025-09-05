import random
import time
from datetime import datetime, timedelta
import json
from market_data_fallback import market_data_generator, get_bulk_market_data

# Educational fallback data for learning purposes
FALLBACK_STOCKS = {
    'RELIANCE': {
        'name': 'Reliance Industries Ltd',
        'sector': 'Oil & Gas',
        'current_price': 2456.75,
        'change_percent': 1.23,
        'market_cap': '16,60,000 Cr'
    },
    'TCS': {
        'name': 'Tata Consultancy Services',
        'sector': 'IT Services', 
        'current_price': 3678.90,
        'change_percent': -0.87,
        'market_cap': '13,40,000 Cr'
    },
    'HDFC': {
        'name': 'HDFC Bank Ltd',
        'sector': 'Banking',
        'current_price': 1567.45,
        'change_percent': 0.56,
        'market_cap': '11,80,000 Cr'
    },
    'INFY': {
        'name': 'Infosys Ltd',
        'sector': 'IT Services',
        'current_price': 1456.30,
        'change_percent': 1.45,
        'market_cap': '6,20,000 Cr'
    },
    'NIFTY': {
        'name': 'Nifty 50',
        'sector': 'Index',
        'current_price': 19847.35,
        'change_percent': 0.78,
        'market_cap': 'Index'
    },
    'SENSEX': {
        'name': 'Sensex',
        'sector': 'Index', 
        'current_price': 66707.20,
        'change_percent': 0.65,
        'market_cap': 'Index'
    },
    'BANKNIFTY': {
        'name': 'Bank Nifty',
        'sector': 'Index',
        'current_price': 45123.80,
        'change_percent': -0.23,
        'market_cap': 'Index'
    }
}

def generate_realistic_candlesticks(symbol, period='1d', days=120):
    """
    Generate educational candlestick data for learning purposes
    This is synthetic data for educational simulation only
    """
    base_price = FALLBACK_STOCKS.get(symbol, {}).get('current_price', 1000)
    
    # Adjust base price for realistic ranges
    if 'NIFTY' in symbol or 'SENSEX' in symbol:
        base_price = base_price
        volatility = 0.015  # 1.5% daily volatility for indices
    else:
        volatility = 0.025  # 2.5% daily volatility for stocks
    
    candles = []
    current_price = base_price * (0.9 + random.random() * 0.2)  # Start within ±10%
    
    # Time intervals based on period
    if period in ['1d', '1D']:
        interval = 300  # 5 min intervals
        total_points = 78  # Trading hours: 6.5 hours * 12 intervals
        start_time = datetime.now().replace(hour=9, minute=15, second=0, microsecond=0)
    elif period in ['1w', '1W', '5d']:
        interval = 3600  # 1 hour intervals  
        total_points = 35  # 5 days * 7 hours
        start_time = datetime.now() - timedelta(days=5)
    elif period in ['1m', '1M', '30d']:
        interval = 86400  # Daily intervals
        total_points = 30
        start_time = datetime.now() - timedelta(days=30)
    elif period in ['3m', '3M']:
        interval = 86400
        total_points = 90
        start_time = datetime.now() - timedelta(days=90)
    else:  # 1y
        interval = 86400
        total_points = 252  # Trading days in a year
        start_time = datetime.now() - timedelta(days=365)
    
    for i in range(total_points):
        timestamp = start_time + timedelta(seconds=i * interval)
        
        # Generate realistic price movement
        daily_return = random.gauss(0, volatility)  # Normal distribution
        trend_factor = 0.0001 * i  # Slight upward trend for educational purpose
        
        open_price = current_price
        close_price = open_price * (1 + daily_return + trend_factor)
        
        # Ensure positive prices
        close_price = max(close_price, open_price * 0.95)
        
        # Generate high and low
        intraday_volatility = volatility * 0.5
        high_price = max(open_price, close_price) * (1 + random.uniform(0, intraday_volatility))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, intraday_volatility))
        
        # Ensure OHLC consistency
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        candle = {
            'time': int(timestamp.timestamp()),
            'open': round(open_price, 2),
            'high': round(high_price, 2), 
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': random.randint(100000, 1000000)
        }
        
        candles.append(candle)
        current_price = close_price
    
    return candles

# New: Bulk data fetcher for multiple symbols
def get_bulk_market_data_endpoint(symbols):
    """
    Efficiently fetch data for multiple symbols using the Indian Stock API
    This reduces API calls by batching requests
    """
    try:
        # Use the enhanced market data generator
        return get_bulk_market_data(symbols)
    except Exception as e:
        print(f"Bulk market data fetch error: {e}")
        # Fallback to individual educational data
        result = {
            'quotes': {},
            'trending': get_market_movers(),
            'news': [],
            'timestamp': time.time(),
            'source': 'educational_fallback'
        }
        
        for symbol in symbols:
            result['quotes'][symbol] = get_stock_quote(symbol)
        
        return result

def get_stock_quote(symbol):
    """
    Enhanced stock quote with API integration
    """
    # Try to get from market data generator (which includes API integration)
    try:
        quote_data = market_data_generator.get_current_price(symbol)
        if quote_data:
            return quote_data
    except Exception as e:
        print(f"API quote fetch error for {symbol}: {e}")
    
    # Existing fallback logic
    if symbol.upper() in FALLBACK_STOCKS:
        stock_data = FALLBACK_STOCKS[symbol.upper()].copy()
        
        # Add some random variation for realism (±2%)
        price_variation = random.uniform(-0.02, 0.02)
        stock_data['current_price'] *= (1 + price_variation)
        stock_data['change_percent'] += random.uniform(-0.5, 0.5)
        
        return {
            'symbol': symbol.upper(),
            'price': round(stock_data['current_price'], 2),
            'change_percent': round(stock_data['change_percent'], 2),
            'name': stock_data['name'],
            'sector': stock_data['sector'],
            'market_cap': stock_data['market_cap'],
            'status': 'success',
            'source': 'educational_data',
            'timestamp': int(time.time())
        }
    
    # Generic fallback for unknown symbols
    return {
        'symbol': symbol.upper(),
        'price': round(random.uniform(100, 5000), 2),
        'change_percent': round(random.uniform(-5, 5), 2),
        'name': f'{symbol.upper()} Ltd',
        'sector': 'Unknown',
        'market_cap': 'N/A',
        'status': 'success',
        'source': 'educational_data',
        'timestamp': int(time.time())
    }

def get_market_movers():
    """
    Get top gainers and losers for educational purposes
    """
    gainers = []
    losers = []
    
    for symbol, data in FALLBACK_STOCKS.items():
        variation = random.uniform(-5, 5)
        quote = get_stock_quote(symbol)
        quote['change_percent'] = variation
        
        if variation > 0:
            gainers.append(quote)
        else:
            losers.append(quote)
    
    gainers.sort(key=lambda x: x['change_percent'], reverse=True)
    losers.sort(key=lambda x: x['change_percent'])
    
    return {
        'gainers': gainers[:5],
        'losers': losers[:5]
    }

# Educational trading scenarios for different age groups
EDUCATIONAL_SCENARIOS = {
    'beginner': {
        'name': 'Basic Trading',
        'description': 'Learn the basics of buying and selling stocks',
        'initial_money': 50000,
        'recommended_stocks': ['TCS', 'RELIANCE', 'HDFC'],
        'lessons': [
            'Start with blue-chip stocks',
            'Understand market orders vs limit orders', 
            'Learn about profit and loss calculations'
        ]
    },
    'intermediate': {
        'name': 'Portfolio Management',
        'description': 'Learn diversification and risk management',
        'initial_money': 100000,
        'recommended_stocks': ['TCS', 'RELIANCE', 'HDFC', 'INFY'],
        'lessons': [
            'Diversify across sectors',
            'Monitor your portfolio regularly',
            'Understand market trends'
        ]
    },
    'advanced': {
        'name': 'Advanced Strategies',
        'description': 'Learn advanced trading concepts',
        'initial_money': 200000,
        'recommended_stocks': list(FALLBACK_STOCKS.keys()),
        'lessons': [
            'Technical analysis basics',
            'Index investing strategies',
            'Risk-reward ratios'
        ]
    }
}

def get_educational_tips():
    """
    Return random educational tips for users
    """
    tips = [
        "💡 Never invest money you cannot afford to lose",
        "📈 Diversification helps reduce risk in your portfolio", 
        "⏰ Time in the market beats timing the market",
        "📚 Always research before investing in any stock",
        "🎯 Set clear investment goals and stick to your plan",
        "📊 Understand the company's fundamentals before buying",
        "⚖️ Balance risk and reward in your investment decisions",
        "💰 Start with small amounts and gradually increase",
        "📋 Keep track of all your transactions and performance",
        "🔍 Stay informed about market news and trends"
    ]
    return random.choice(tips)
