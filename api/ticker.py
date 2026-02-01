from http.server import BaseHTTPRequestHandler
import json
import yfinance as yf
from urllib.parse import parse_qs, urlparse

def format_number(value, decimals=2):
    """Format number with specified decimal places"""
    if value is None:
        return None
    try:
        return round(float(value), decimals)
    except (ValueError, TypeError):
        return None

def format_billions(value):
    """Format large numbers in billions with B$ suffix"""
    if value is None:
        return None
    try:
        billions = float(value) / 1_000_000_000
        return f"{round(billions, 2)}B$"
    except (ValueError, TypeError):
        return None

def format_percentage(value):
    """Format decimal as percentage"""
    if value is None:
        return None
    try:
        return f"{round(float(value) * 100, 2)}%"
    except (ValueError, TypeError):
        return None

def calculate_change(current, previous):
    """Calculate percentage change"""
    if current is None or previous is None:
        return None
    try:
        current = float(current)
        previous = float(previous)
        if previous == 0:
            return None
        change = ((current - previous) / previous) * 100
        return round(change, 2)
    except (ValueError, TypeError):
        return None

# IMPORTANT: The class must be named exactly "handler" (lowercase)
class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        # Set CORS headers first
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Parse query parameters
            query = urlparse(self.path).query
            params = parse_qs(query)
            
            # Get ticker symbol
            ticker_symbol = params.get('ticker', ['AAPL'])[0]
            
            # Fetch ticker info
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            # Simple response for testing
            result = {
                "ticker": ticker_symbol.upper(),
                "price": format_number(info.get('currentPrice'), 2),
                "marketCap": format_billions(info.get('marketCap')),
                "success": True
            }
            
            self.wfile.write(json.dumps(result, indent=2).encode())
            
        except Exception as e:
            error_response = {
                "error": str(e),
                "success": False
            }
            self.wfile.write(json.dumps(error_response).encode())
