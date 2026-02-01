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
        return f"{round(billions, 3)} B$"
    except (ValueError, TypeError):
        return None

def format_millions(value):
    """Format numbers in millions with M$ suffix"""
    if value is None:
        return None
    try:
        millions = float(value) / 1_000_000
        return f"{round(millions, 2)} Mill."
    except (ValueError, TypeError):
        return None

def format_percentage(value):
    """Format decimal as percentage"""
    if value is None:
        return None
    try:
        return f"{round(float(value) * 100, 2)} %"
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
            
            
            # Calculate one day change
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
            one_day_change = calculate_change(current_price, previous_close)
            
            # Calculate 52 week change percentage
            fifty_two_week_change = info.get('52WeekChange')
            fifty_two_week_change_pct = format_percentage(fifty_two_week_change) if fifty_two_week_change else None
            
            # Organize data into structured categories
            organized_data = {
                "ticker": ticker_symbol.upper(),
                "timestamp": info.get('regularMarketTime'),
                
                "main_info": {
                    "symbol": info.get('symbol'),
                    "shortName": info.get('shortName'),
                    "sector": info.get('sector'),
                    "industry": info.get('industry'),
                    "currency": info.get('currency'),
                    "currentPrice": format_number(current_price, 2),
                    "oneDayChange": f"{one_day_change}%" if one_day_change is not None else None,
                    "fiftyTwoWeekChange": fifty_two_week_change_pct
                    "marketCap": format_billions(info.get('marketCap')),
                    "PS": format_number(info.get('priceToSalesTrailing12Months'), 2),
                    "PE": format_number(info.get('trailingPE'), 2),
                    "forwardPE": format_number(info.get('forwardPE'), 2),
                    "recommendation": info.get('recommendationKey'),
                    "PT_Low": format_number(info.get('targetLowPrice'), 2),
                    "PT_High": format_number(info.get('targetHighPrice'), 2),
                },
                
                "company_info": {
                    "website": info.get('website'),
                    "address1": info.get('address1'),
                    "city": info.get('city'),
                    "state": info.get('state'),
                    "zip": info.get('zip'),
                    "country": info.get('country'),
                    "phone": info.get('phone'),
                    "sector": info.get('sector'),
                    "industry": info.get('industry'),
                    "industryKey": info.get('industryKey'),
                    "sectorKey": info.get('sectorKey'),
                    "fullTimeEmployees": info.get('fullTimeEmployees')
                },
                
                "valuation": {
                    "marketCap": format_billions(info.get('marketCap')),
                    "enterpriseValue": format_billions(info.get('enterpriseValue')),
                    "priceToBook": format_number(info.get('priceToBook'), 2),
                    "priceToSalesTrailing12Months": format_number(info.get('priceToSalesTrailing12Months'), 2),
                    "enterpriseToRevenue": format_number(info.get('enterpriseToRevenue'), 2),
                    "enterpriseToEbitda": format_number(info.get('enterpriseToEbitda'), 2),
                    "bookValue": format_number(info.get('bookValue'), 2),
                    "sharesOutstanding": format_millions(info.get('sharesOutstanding')),
                    "floatShares": format_millions(info.get('floatShares')),
                    "impliedSharesOutstanding": format_millions(info.get('impliedSharesOutstanding'))
                },
                
                "ratios": {
                    "trailingPE": format_number(info.get('trailingPE'), 2),
                    "forwardPE": format_number(info.get('forwardPE'), 2),
                    "pegRatio": format_number(info.get('pegRatio'), 2),
                    "priceToBook": format_number(info.get('priceToBook'), 2),
                    "priceToSalesTrailing12Months": format_number(info.get('priceToSalesTrailing12Months'), 2),
                    "profitMargins": format_percentage(info.get('profitMargins')),
                    "operatingMargins": format_percentage(info.get('operatingMargins')),
                    "returnOnAssets": format_percentage(info.get('returnOnAssets')),
                    "returnOnEquity": format_percentage(info.get('returnOnEquity')),
                    "currentRatio": format_number(info.get('currentRatio'), 2),
                    "quickRatio": format_number(info.get('quickRatio'), 2),
                    "debtToEquity": format_number(info.get('debtToEquity'), 2)
                },
                
                "returns": {
                    "returnOnAssets": format_percentage(info.get('returnOnAssets')),
                    "returnOnEquity": format_percentage(info.get('returnOnEquity')),
                    "profitMargins": format_percentage(info.get('profitMargins')),
                    "operatingMargins": format_percentage(info.get('operatingMargins')),
                    "grossMargins": format_percentage(info.get('grossMargins')),
                    "ebitdaMargins": format_percentage(info.get('ebitdaMargins'))
                },
                
                "growth": {
                    "revenueGrowth": format_percentage(info.get('revenueGrowth')),
                    "earningsGrowth": format_percentage(info.get('earningsGrowth')),
                    "earningsQuarterlyGrowth": format_percentage(info.get('earningsQuarterlyGrowth')),
                    "revenuePerShare": format_number(info.get('revenuePerShare'), 2),
                    "totalRevenue": format_billions(info.get('totalRevenue')),
                    "earningsPerShare": format_number(info.get('trailingEps'), 2),
                    "forwardEps": format_number(info.get('forwardEps'), 2),
                    "bookValue": format_number(info.get('bookValue'), 2),
                    "priceToBook": format_number(info.get('priceToBook'), 2),
                    "enterpriseValue": format_billions(info.get('enterpriseValue')),
                    "pegRatio": format_number(info.get('pegRatio'), 2),
                    "trailingPegRatio": format_number(info.get('trailingPegRatio'), 2)
                },
                
                "price_performance": {
                    "currentPrice": format_number(current_price, 2),
                    "previousClose": format_number(previous_close, 2),
                    "open": format_number(info.get('open'), 2),
                    "dayLow": format_number(info.get('dayLow'), 2),
                    "dayHigh": format_number(info.get('dayHigh'), 2),
                    "regularMarketPreviousClose": format_number(info.get('regularMarketPreviousClose'), 2),
                    "fiftyTwoWeekLow": format_number(info.get('fiftyTwoWeekLow'), 2),
                    "fiftyTwoWeekHigh": format_number(info.get('fiftyTwoWeekHigh'), 2),
                    "fiftyDayAverage": format_number(info.get('fiftyDayAverage'), 2),
                    "twoHundredDayAverage": format_number(info.get('twoHundredDayAverage'), 2),
                    "52WeekChange": fifty_two_week_change_pct,
                    "SandP52WeekChange": format_percentage(info.get('SandP52WeekChange'))
                },
                
                "risk": {
                    "beta": format_number(info.get('beta'), 2),
                    "beta3Year": format_number(info.get('beta3Year'), 2),
                    "overallRisk": info.get('overallRisk'),
                    "auditRisk": info.get('auditRisk'),
                    "boardRisk": info.get('boardRisk'),
                    "compensationRisk": info.get('compensationRisk'),
                    "shareHolderRightsRisk": info.get('shareHolderRightsRisk')
                },
                
                "debt": {
                    "totalDebt": format_billions(info.get('totalDebt')),
                    "totalCash": format_billions(info.get('totalCash')),
                    "totalCashPerShare": format_number(info.get('totalCashPerShare'), 2),
                    "debtToEquity": format_number(info.get('debtToEquity'), 2),
                    "currentRatio": format_number(info.get('currentRatio'), 2),
                    "quickRatio": format_number(info.get('quickRatio'), 2),
                    "freeCashflow": format_billions(info.get('freeCashflow')),
                    "operatingCashflow": format_billions(info.get('operatingCashflow'))
                },
                
                "trading_info": {
                    "volume": info.get('volume'),
                    "regularMarketVolume": info.get('regularMarketVolume'),
                    "averageVolume": info.get('averageVolume'),
                    "averageVolume10days": info.get('averageVolume10days'),
                    "averageDailyVolume10Day": info.get('averageDailyVolume10Day'),
                    "bid": format_number(info.get('bid'), 2),
                    "ask": format_number(info.get('ask'), 2),
                    "bidSize": info.get('bidSize'),
                    "askSize": info.get('askSize'),
                    "fiftyDayAverage": format_number(info.get('fiftyDayAverage'), 2),
                    "twoHundredDayAverage": format_number(info.get('twoHundredDayAverage'), 2),
                    "change_from_50DMA": f"{calculate_change(current_price, info.get('fiftyDayAverage'))}%" if calculate_change(current_price, info.get('fiftyDayAverage')) else None,
                    "change_from_200DMA": f"{calculate_change(current_price, info.get('twoHundredDayAverage'))}%" if calculate_change(current_price, info.get('twoHundredDayAverage')) else None,
                    "oneDayChange": f"{one_day_change}%" if one_day_change is not None else None
                },
                
                "price_targets": {
                    "targetHighPrice": format_number(info.get('targetHighPrice'), 2),
                    "targetLowPrice": format_number(info.get('targetLowPrice'), 2),
                    "targetMeanPrice": format_number(info.get('targetMeanPrice'), 2),
                    "targetMedianPrice": format_number(info.get('targetMedianPrice'), 2),
                    "recommendationMean": format_number(info.get('recommendationMean'), 2),
                    "recommendationKey": info.get('recommendationKey'),
                    "numberOfAnalystOpinions": info.get('numberOfAnalystOpinions')
                },
                
                "dividends": {
                    "dividendRate": format_number(info.get('dividendRate'), 2),
                    "dividendYield": format_percentage(info.get('dividendYield')),
                    "exDividendDate": info.get('exDividendDate'),
                    "payoutRatio": format_percentage(info.get('payoutRatio')),
                    "fiveYearAvgDividendYield": format_percentage(info.get('fiveYearAvgDividendYield')),
                    "trailingAnnualDividendRate": format_number(info.get('trailingAnnualDividendRate'), 2),
                    "trailingAnnualDividendYield": format_percentage(info.get('trailingAnnualDividendYield'))
                },
                
                "earnings": {
                    "trailingEps": format_number(info.get('trailingEps'), 2),
                    "forwardEps": format_number(info.get('forwardEps'), 2),
                    "mostRecentQuarter": info.get('mostRecentQuarter'),
                    "netIncomeToCommon": format_billions(info.get('netIncomeToCommon')),
                    "trailingPegRatio": format_number(info.get('trailingPegRatio'), 2)
                }
            }
            
                "company_business": {
                    "logo_url": info.get('logo_url'),
                    "shortName": info.get('shortName'),
                    "longBusinessSummary": info.get('longBusinessSummary'),
                    "sector": info.get('sector'),
                    "industry": info.get('industry'),
                    "website": info.get('website'),
                },
                
            
            # Send response
            self.wfile.write(json.dumps(organized_data, indent=2).encode())
            
            
        except Exception as e:
            error_response = {
                "error": str(e),
                "success": False
            }
            self.wfile.write(json.dumps(error_response).encode())
