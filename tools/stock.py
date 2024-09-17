import numpy as np
import discord
from discord.ext import commands
import yfinance as yf
import mplfinance as mpf
import io


def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = np.zeros_like(gain)
    avg_loss = np.zeros_like(loss)

    avg_gain[period] = np.mean(gain[:period])
    avg_loss[period] = np.mean(loss[:period])

    for i in range(period + 1, len(gain)):
        avg_gain[i] = (avg_gain[i - 1] * (period - 1) + gain[i]) / period
        avg_loss[i] = (avg_loss[i - 1] * (period - 1) + loss[i]) / period

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_stock_candlestick(symbol, period='1mo'):
    # 從 yfinance 取得股票資料
    stock_data = yf.download(symbol, period=period)
    
    if stock_data.empty:
        return None

    # 將日期設置為索引
    stock_data.index.name = 'Date'

    # 定義自訂的市場顏色
    mc = mpf.make_marketcolors(
        up='red',    # 上漲的蠟燭顏色
        down='green',  # 下跌的蠟燭顏色
        edge='inherit',
        wick='inherit',
        volume='in'
    )

    # 定義自訂的圖表風格
    s = mpf.make_mpf_style(marketcolors=mc)

    # 使用 mplfinance 繪製 K 線圖
    img_buffer = io.BytesIO()
    mpf.plot(stock_data, type='candle', volume=True, style=s, savefig=img_buffer)
    img_buffer.seek(0)
    return img_buffer