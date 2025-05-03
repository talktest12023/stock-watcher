import csv
import yfinance as yf
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import Stock
import pandas as pd
from scipy.stats import zscore

def get_stock_data(request):
    tickers = request.GET.getlist('ticker')  # Supports multiple tickers
    if not tickers:
        return JsonResponse({'error': 'No tickers provided'}, status=400)

    result = {"stocks": {}}

    for ticker in tickers:
        try:
            data = yf.download(ticker, period='6mo', interval='1d', progress=False)
            data.reset_index(inplace=True)
            if isinstance(data.columns, pd.MultiIndex):
                close_prices = data[('Close', ticker)]
                volumes = data[('Volume', ticker)]
                anomalies=((zscore(data[('Close', ticker)]) >= 2) | (zscore(data[('Close', ticker)]) <= -2)).tolist()

            else:
                close_prices = data['Close']
                volumes = data['Volume']
                anomalies=((zscore(data['Close']) >= 2)| (zscore(data['Close']) <=-2)).tolist()


            result["stocks"][ticker] = {
                'dates': data['Date'].dt.strftime('%Y-%m-%d').tolist(),
                'closing_prices': close_prices.round(2).tolist(),
                'volumes': volumes.tolist(),
                'anomalies':anomalies
            }
        except Exception as e:
            result["stocks"][ticker] = {"error": str(e)}

    return JsonResponse(result)


def stock_view(request):
    data = []
    selected_tickers = []
    form_submitted = False
    comparison_data = []

    if request.method == "POST":
        print(request.POST.getlist("ticker[]"))
        selected_tickers = request.POST.getlist("ticker[]")  # ✅ Handles multiple
        form_submitted = 'fetch_data' in request.POST

        for ticker in selected_tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            info = stock.info
            rows = hist.reset_index()[["Date", "Close", "Volume"]].copy()
            rows["Ticker"] = ticker  # ✅ Add ticker column to distinguish
            # ✅ Z-score calculation
            if len(rows) >= 2:
                rows["Z_Score_Close"] = zscore(rows["Close"])
                rows["Z_Score_Volume"] =zscore(rows["Volume"])

            else:
                rows["Z_Score_Close"] = 0  # fallback if not enough data
                rows["Z_Score_Volume"] = 0  # fallback if not enough data
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
            response["Content-Disposition"] = 'attachment; filename="stock_data.csv"'

            writer = csv.writer(response)
            writer.writerow(["Ticker", "Date", "Close", "Volume","Z-Score-Close-Price","Z-Score-Close-Volume"])
            for row in data:
                writer.writerow([row["Ticker"], row["Date"], row["Close"], row["Volume"],row["Z_Score_Close"],row["Z_Score_Volume"]])
            return respons
    print(data)
    context = {
        "tickers": Stock.objects.all(),
        "data": data,
        "selected_ticker": selected_tickers,  # now a list
        'form_submitted': form_submitted,
        "comparison_data": comparison_data,
    }
    return render(request, "stocks/stock_view.html", context)


def chart_view(request):
    return render(request, 'chart.html')

