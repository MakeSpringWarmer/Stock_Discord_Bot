import yfinance as yf
from discord.ext import commands
from tools.stock import calculate_rsi, get_stock_candlestick
import discord


class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def daily(self, ctx, ticker: str):
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")

        if data.empty:
            await ctx.send(f"無法找到代號為 {ticker} 的股票資訊。")
            return

        # 提取所需的股票信息
        last_quote = data.iloc[0]

        embed = discord.Embed(
            title=f"{ticker} 當日股票資訊",
            description=f"股票代號: {ticker}",
            color=discord.Color.blue(),  # 可以選擇其他顏色
        )

        embed.add_field(name="日期", value=last_quote.name.date(), inline=False)
        embed.add_field(name="開盤價", value=f"{last_quote['Open']:.2f}", inline=True)
        embed.add_field(name="最高價", value=f"{last_quote['High']:.2f}", inline=True)
        embed.add_field(name="最低價", value=f"{last_quote['Low']:.2f}", inline=True)
        embed.add_field(name="收盤價", value=f"{last_quote['Close']:.2f}", inline=True)
        embed.add_field(name="成交量", value=f"{last_quote['Volume']:,}", inline=True)

        # 發送嵌入消息
        await ctx.send(embed=embed)

    @commands.command()
    async def rsi(self, ctx, ticker: str):
        stock = yf.Ticker(ticker)
        data = stock.history(period="1mo")

        if data.empty:
            await ctx.send(f"無法找到代號為 {ticker} 的股票資訊。")
            return

        rsi_10 = calculate_rsi(data, period=10)
        rsi_5 = calculate_rsi(data, period=5)

        rsi_10_value = rsi_10[-1]
        rsi_5_value = rsi_5[-1]

        embed = discord.Embed(
            title=f"{ticker} RSI 資訊",
            description=f"股票代號: {ticker}",
            color=discord.Color.green(),  # 可以選擇其他顏色
        )

        embed.add_field(name="10天 RSI", value=f"{rsi_10_value:.2f}", inline=True)
        embed.add_field(name="5天 RSI", value=f"{rsi_5_value:.2f}", inline=True)

        # 發送嵌入消息
        await ctx.send(embed=embed)

    @commands.command()
    async def month(self, ctx, symbol: str):
        img_buffer = get_stock_candlestick(symbol)

        if img_buffer is None:
            await ctx.send(f"無法取得 {symbol} 的資料。")
        else:
            picture = discord.File(fp=img_buffer, filename=f"{symbol}_candlestick.png")
            await ctx.send(file=picture)


async def setup(bot):
    await bot.add_cog(Stock(bot))
