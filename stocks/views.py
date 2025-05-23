import csv
import yfinance as yf
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Stock
import pandas as pd
from scipy.stats import zscore
from django.core.cache import cache
import numpy as np
from datetime import date, timedelta


def get_stock_data(request):
    tickers = request.GET.getlist('ticker')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if not tickers:
        return JsonResponse({'error': 'No tickers provided'}, status=400)

    result = {"stocks": {}}

    for ticker in tickers:
        try:
            cache_key = f"{ticker}_6mo_data"
            data = cache.get(cache_key)

            if data is None:
                if start_date and end_date:
                    data = yf.download(ticker, start=start_date, end=end_date, interval='1d', progress=False)
                else:
                    data = yf.download(ticker, period='6mo', interval='1d', progress=False)
                cache.set(cache_key, data, timeout=3600)

            data.reset_index(inplace=True)

            # ✅ Handle both MultiIndex and flat DataFrame
            if isinstance(data.columns, pd.MultiIndex):
                open_prices = data[('Open', ticker)]
                high_prices = data[('High', ticker)]
                low_prices = data[('Low', ticker)]
                close_prices = data[('Close', ticker)]
                volumes = data[('Volume', ticker)]
            else:
                open_prices = data['Open']
                high_prices = data['High']
                low_prices = data['Low']
                close_prices = data['Close']
                volumes = data['Volume']

            # Z-score anomalies
            z_close = zscore(close_prices.fillna(0))
            z_volume = zscore(volumes.fillna(0))
            anomalies_close = ((z_close >= 2) | (z_close <= -2)).tolist()
            anomalies_volume = ((z_volume >= 2) | (z_volume <= -2)).tolist()

            # SMA
            sma_20_series = close_prices.rolling(window=20).mean().fillna(0)
            sma_50_series = close_prices.rolling(window=50).mean().fillna(0)
            sma_20 = sma_20_series.round(2).tolist()
            sma_50 = sma_50_series.round(2).tolist()

            # MACD
            ema_12 = close_prices.ewm(span=12, adjust=False).mean()
            ema_26 = close_prices.ewm(span=26, adjust=False).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_hist = macd_line - signal_line

            # RSI
            delta = close_prices.diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsi = rsi.round(2).fillna(0)

            # Golden/Death Crosses
            golden_crosses = []
            death_crosses = []
            for i in range(1, len(close_prices)):
                if pd.notna(sma_20_series[i]) and pd.notna(sma_50_series[i]) and pd.notna(sma_20_series[i - 1]) and pd.notna(sma_50_series[i - 1]):
                    prev_diff = sma_20_series[i - 1] - sma_50_series[i - 1]
                    curr_diff = sma_20_series[i] - sma_50_series[i]
                    if prev_diff < 0 and curr_diff >= 0:
                        golden_crosses.append(i)
                    elif prev_diff > 0 and curr_diff <= 0:
                        death_crosses.append(i)

            # ✅ Clean OHLC array for candlestick chart
            dates = data['Date'].dt.strftime('%Y-%m-%d')
            ohlc = [
                {"x": date, "o": float(o), "h": float(h), "l": float(l), "c": float(c)}
                for date, o, h, l, c in zip(dates, open_prices, high_prices, low_prices, close_prices)
            ]

            # Final JSON for this stock
            result["stocks"][ticker] = {
                'dates': dates.tolist(),
                'closing_prices': close_prices.round(2).tolist(),
                'volumes': volumes.tolist(),
                'anomalies_close': anomalies_close,
                'anomalies_volume': anomalies_volume,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'golden_crosses': golden_crosses,
                'death_crosses': death_crosses,
                'macd_line': macd_line.round(2).fillna(0).tolist(),
                'signal_line': signal_line.round(2).fillna(0).tolist(),
                'macd_histogram': macd_hist.round(2).fillna(0).tolist(),
                'RSI': rsi.tolist(),
                'ohlc': ohlc,
            }

        except Exception as e:
            result["stocks"][ticker] = {"error": str(e)}

    return JsonResponse(result)


def fetch_stock_dataframe(ticker, start_date=None, end_date=None):
    try:
        if start_date and end_date:
            df = yf.download(ticker, start=start_date, end=end_date, interval='1d', progress=False)
        else:
            df = yf.download(ticker, period='6mo', interval='1d', progress=False)
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None


def stock_view(request):
    data = []
    selected_tickers = []
    form_submitted = False
    comparison_data = []
    price_alerts = []  # ✅ initialize here to fix the error

    if request.method == "POST":
        selected_tickers = request.POST.getlist("ticker[]")
        form_submitted = 'fetch_data' in request.POST
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        upper_limit = request.POST.get('upper_limit')
        lower_limit = request.POST.get('lower_limit')
        if upper_limit:
            upper_limit = float(upper_limit)
        if lower_limit:
            lower_limit = float(lower_limit)
        #price_alerts = []
        for ticker in selected_tickers:
            df = fetch_stock_dataframe(ticker, start_date, end_date)
            if df is not None and not df.empty:
                latest_price = df['Close'].iloc[-1]
                alert_type = None
                if upper_limit and latest_price >= upper_limit:
                    alert_type = '🔺 Price above upper limit'
                elif lower_limit and latest_price <= lower_limit:
                    alert_type = '🔻 Price below lower limit'

                if alert_type:
                    price_alerts.append({
                    'ticker': ticker,
                    'latest_price': latest_price,
                    'alert': alert_type,
                    })

            print("price alert print",price_alerts)
            # Optional: Pass to template or use for alerting logic
            #context['price_alerts'] = price_alerts
            stock = yf.Ticker(ticker)

            # ✅ Cache history
            hist_cache_key = f"{ticker}_5d_history"
            hist = cache.get(hist_cache_key)
            if hist is None or hist.empty:
                hist = stock.history(period="5d")
                cache.set(hist_cache_key, hist, timeout=3600)

            # ✅ Cache info
            info_cache_key = f"{ticker}_info"
            info = cache.get(info_cache_key)
            if not info:
                info = stock.info
                cache.set(info_cache_key, info, timeout=3600)

            rows = hist.reset_index()[["Date", "Close", "Volume"]].copy()
            rows["Ticker"] = ticker

            if len(rows) >= 2:
                rows["Z_Score_Close"] = zscore(rows["Close"])
                rows["Z_Score_Volume"] = zscore(rows["Volume"])
            else:
                rows["Z_Score_Close"] = 0
                rows["Z_Score_Volume"] = 0

            data.extend(rows.to_dict(orient="records"))

            def safe_get(key):
                return round(info.get(key, 0), 2) if isinstance(info.get(key), (int, float)) else info.get(key, 'N/A')

            comparison_data.append({
                'ticker': ticker,
                'market_cap': safe_get('marketCap'),
                'pe_ratio': safe_get('trailingPE'),
                'roe': round(info.get('returnOnEquity', 0) * 100, 2) if info.get('returnOnEquity') else 'N/A',
                'eps': safe_get('epsTrailingTwelveMonths'),
                'de_ratio': safe_get('debtToEquity'),
            })

        if "export_csv" in request.POST and selected_tickers:
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename=\"stock_data.csv\"'

            writer = csv.writer(response)
            writer.writerow(["Ticker", "Date", "Close", "Volume", "Z-Score-Close-Price", "Z-Score-Close-Volume"])
            for row in data:
                writer.writerow([row["Ticker"], row["Date"], row["Close"], row["Volume"], row["Z_Score_Close"], row["Z_Score_Volume"]])
            return response

    context = {
        "tickers": Stock.objects.all(),
        "data": data,
        "selected_ticker": selected_tickers,
        'form_submitted': form_submitted,
        "comparison_data": comparison_data,
        "today": date.today().isoformat(),
        "today_minus_30": (date.today() - timedelta(days=30)).isoformat(),
        "price_alerts": price_alerts,  # ✅ add it here
    }
    return render(request, "stocks/stock_view.html", context)


def chart_view(request):
    return render(request, 'chart.html')
