from django.db import models

# Create your models here.
class Stock(models.Model):
    TICKER_CHOICES = [
    ('ADANIENT.NS', 'Adani Enterprises'),
    ('ADANIPORTS.NS', 'Adani Ports'),
    ('ASIANPAINT.NS', 'Asian Paints'),
    ('AXISBANK.NS', 'Axis Bank'),
    ('BAJAJ-AUTO.NS', 'Bajaj Auto'),
    ('BAJFINANCE.NS', 'Bajaj Finance'),
    ('BAJAJFINSV.NS', 'Bajaj Finserv'),
    ('BHARTIARTL.NS', 'Bharti Airtel'),
    ('BPCL.NS', 'Bharat Petroleum'),
    ('BRITANNIA.NS', 'Britannia'),
    ('CIPLA.NS', 'Cipla'),
    ('COALINDIA.NS', 'Coal India'),
    ('DIVISLAB.NS', 'Divi’s Labs'),
    ('DRREDDY.NS', 'Dr. Reddy’s'),
    ('EICHERMOT.NS', 'Eicher Motors'),
    ('GRASIM.NS', 'Grasim'),
    ('HCLTECH.NS', 'HCL Technologies'),
    ('HDFCBANK.NS', 'HDFC Bank'),
    ('HDFC.NS', 'HDFC'),
    ('HEROMOTOCO.NS', 'Hero MotoCorp'),
    ('HINDALCO.NS', 'Hindalco'),
    ('HINDUNILVR.NS', 'Hindustan Unilever'),
    ('ICICIBANK.NS', 'ICICI Bank'),
    ('INDUSINDBK.NS', 'IndusInd Bank'),
    ('INFY.NS', 'Infosys'),
    ('ITC.NS', 'ITC'),
    ('JSWSTEEL.NS', 'JSW Steel'),
    ('KOTAKBANK.NS', 'Kotak Mahindra Bank'),
    ('LT.NS', 'Larsen & Toubro'),
    ('M&M.NS', 'Mahindra & Mahindra'),
    ('MARUTI.NS', 'Maruti Suzuki'),
    ('NESTLEIND.NS', 'Nestle India'),
    ('NTPC.NS', 'NTPC'),
    ('ONGC.NS', 'ONGC'),
    ('POWERGRID.NS', 'Power Grid'),
    ('RELIANCE.NS', 'Reliance Industries'),
    ('SBILIFE.NS', 'SBI Life Insurance'),
    ('SBIN.NS', 'State Bank of India'),
    ('SHREECEM.NS', 'Shree Cement'),
    ('SUNPHARMA.NS', 'Sun Pharma'),
    ('TATACONSUM.NS', 'Tata Consumer'),
    ('TATAMOTORS.NS', 'Tata Motors'),
    ('TATASTEEL.NS', 'Tata Steel'),
    ('TCS.NS', 'TCS'),
    ('TECHM.NS', 'Tech Mahindra'),
    ('TITAN.NS', 'Titan Company'),
    ('ULTRACEMCO.NS', 'UltraTech Cement'),
    ('UPL.NS', 'UPL'),
    ('WIPRO.NS', 'Wipro')
    ]
    ticker=models.CharField(max_length=50,choices=TICKER_CHOICES)

    def __str__(self):
    	return self.ticker
