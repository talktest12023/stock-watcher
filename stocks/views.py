import csv
import yfinance as yf
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import Stock
import pandas as pd

def get_stock_data(request):
    ticker = request.GET.get('ticker')
    if not ticker:
        return JsonResponse({'error': 'Ticker not provided'}, status=400)

    data = yf.download(ticker, period='6mo', interval='1d')  # 6 months data
    data.reset_index(inplace=True)
    # Check column structure
    if isinstance(data.columns, pd.MultiIndex):
        close_prices = data[('Close', ticker)]
    else:
        close_prices = data['Close']
    result = {
        'dates': data['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'closing_prices':close_prices.round(2).tolist()
    }
    #print("[DEBUG] API Response:", data["Date"].dt.strftime('%Y-%m-%d').tolist())  # ✅ logs in terminal
    #print("[DEBUG] API Response:", data["Close"].round(2).tolist())  # ✅ logs in terminal
    #print(data)
    #closing_series = data[("Close",ticker)].round(2).tolist()  # ✅ This gives you a Series
    #print(type(closing_series))  # Should show: <class 'pandas.core.series.Series'>

    return JsonResponse(result)

def stock_view(request):
    data = None
    selected_ticker = None
    form_submitted = False

    if request.method == "POST":
        selected_ticker = request.POST.get("ticker")
        form_submitted = 'fetch_data' in request.POST

        if selected_ticker:
            stock = yf.Ticker(selected_ticker)
            hist = stock.history(period="5d")
            data = hist.reset_index()[["Date", "Close", "Volume"]].to_dict(orient="records")

            # Handle CSV export
            if "export_csv" in request.POST:
                response = HttpResponse(content_type="text/csv")
                response["Content-Disposition"] = f'attachment; filename="{selected_ticker}_stock_data.csv"'

                writer = csv.writer(response)
                writer.writerow(["Date", "Close", "Volume"])
                for row in data:
                    writer.writerow([row["Date"], row["Close"], row["Volume"]])
                return response

    context = {
        "tickers": Stock.objects.all(),
        "data": data,
        "selected_ticker": selected_ticker,
        'form_submitted': form_submitted,
    }
    return render(request, "stocks/stock_view.html", context)


def chart_view(request):
    return render(request, 'chart.html')

