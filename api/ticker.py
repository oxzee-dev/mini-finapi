from http.server import BaseHTTPRequestHandler
import json
import yfinance as yf
from urllib.parse import parse_qs, urlparse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse query parameters
            query = urlparse(self.path).query
            params = parse_qs(query)
            
            # Get ticker symbol from query params
            ticker_symbol = params.get('ticker', [''])[0]
            
            if not ticker_symbol:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Missing ticker parameter'
                }).encode())
                return
            
            # Fetch ticker info
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            # Remove employee data if present
            info.pop('companyOfficers', None)
            info.pop('fullTimeEmployees', None)
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(info, indent=2).encode())
            
        except Exception as e:
            # Handle errors
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': str(e)
            }).encode())
```

**`requirements.txt`**:
```
yfinance==0.2.40
