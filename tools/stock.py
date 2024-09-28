import numpy as np
import discord
from discord.ext import commands
import yfinance as yf
import mplfinance as mpf
import io
import talib


def calculate_rsi(data, period=14):
    delta = data["Close"].diff()
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


def get_stock_candlestick(symbol, period="1mo"):
    # 從 yfinance 取得股票資料
    stock_data = yf.download(symbol, period=period)

    if stock_data.empty:
        return None

    # 將日期設置為索引
    stock_data.index.name = "Date"

    # 定義自訂的市場顏色
    mc = mpf.make_marketcolors(
        up="red",  # 上漲的蠟燭顏色
        down="green",  # 下跌的蠟燭顏色
        edge="inherit",
        wick="inherit",
        volume="in",
    )

    # 定義自訂的圖表風格
    s = mpf.make_mpf_style(
        marketcolors=mc,
        facecolor="black",  # 圖表背景色
        edgecolor="white",  # 圖表邊框色
        figcolor="black",  # 整個圖形的背景色
        rc={
            "axes.labelcolor": "white",  # 座標軸標籤顏色
            "xtick.color": "white",  # x軸刻度顏色
            "ytick.color": "white",  # y軸刻度顏色
            "axes.edgecolor": "white",  # 座標軸邊框顏色
            "text.color": "white",  # 圖表文字顏色
        },
    )

    # 使用 mplfinance 繪製 K 線圖
    img_buffer = io.BytesIO()
    mpf.plot(stock_data, type="candle", volume=True, style=s, savefig=img_buffer)
    img_buffer.seek(0)
    return img_buffer


def get_stock_chart(symbol, period="3mo"):
    try:
        stock_data = yf.download(symbol, period=period)
        if stock_data.empty:
            print(f"No data downloaded for symbol: {symbol}")
            return None

        stock_data.index.name = "Date"

        # 計算技術指標
        stock_data["MA5"] = stock_data["Close"].rolling(window=5).mean()
        stock_data["MA20"] = stock_data["Close"].rolling(window=20).mean()
        (
            stock_data["upper_band"],
            stock_data["middle_band"],
            stock_data["lower_band"],
        ) = talib.BBANDS(stock_data["Close"], timeperiod=30)
        stock_data["MACD"], stock_data["MACD_signal"], stock_data["MACD_hist"] = (
            talib.MACD(stock_data["Close"])
        )

        # 刪除包含 NaN 的行
        stock_data.dropna(inplace=True)

        if stock_data.empty:
            print("Not enough data after calculating indicators.")
            return None

        # 自訂顏色和樣式
        mc = mpf.make_marketcolors(
            up="red",  # 上漲的蠟燭顏色
            down="green",  # 下跌的蠟燭顏色
            edge="inherit",  # 蠟燭邊框顏色繼承
            wick="inherit",  # 蠟燭影線顏色繼承
            volume="in",  # 成交量顏色繼承蠟燭顏色
        )

        # 設定圖表樣式，將背景設為黑色，調整其他元素顏色
        s = mpf.make_mpf_style(
            marketcolors=mc,
            facecolor="black",  # 圖表背景顏色
            edgecolor="black",  # 圖表邊框顏色
            figcolor="black",  # 圖片背景顏色
            gridcolor="gray",  # 網格線顏色
            gridstyle="--",  # 網格線樣式
            rc={
                "font.size": 10,  # 字體大小
                "text.color": "white",  # 文字顏色
                "axes.labelcolor": "white",  # 軸標籤顏色
                "xtick.color": "white",  # X 軸刻度顏色
                "ytick.color": "white",  # Y 軸刻度顏色
            },
        )

        # 調整技術指標顏色，以適應黑色背景
        apds = [
            mpf.make_addplot(stock_data["MA5"], color="lightblue"),
            mpf.make_addplot(stock_data["MA20"], color="orange"),
            mpf.make_addplot(stock_data["upper_band"], color="yellow"),
            mpf.make_addplot(stock_data["middle_band"], color="magenta"),
            mpf.make_addplot(stock_data["lower_band"], color="yellow"),
            mpf.make_addplot(
                stock_data["MACD"], panel=1, color="lightgreen", title="MACD"
            ),
            mpf.make_addplot(stock_data["MACD_signal"], panel=1, color="cyan"),
            mpf.make_addplot(
                stock_data["MACD_hist"], type="bar", panel=1, color="gray"
            ),
        ]

        img_buffer = io.BytesIO()
        mpf.plot(
            stock_data,
            type="candle",
            volume=True,
            style=s,
            addplot=apds,
            panel_ratios=(6, 3),
            savefig=dict(fname=img_buffer, dpi=100, bbox_inches="tight"),
        )
        img_buffer.seek(0)

        return img_buffer

    except Exception as e:
        print(f"An error occurred in get_stock_chart: {e}")
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
