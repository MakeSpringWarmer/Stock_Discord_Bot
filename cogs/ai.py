from discord.ext import commands
import google.generativeai as genai
import os


class Ai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.api_key = os.environ["GEMINI_API_KEY"]
            if self.api_key:
                genai.configure(api_key=self.api_key)
            else:
                print("API_KEY_NOT_FOUND")
        except KeyError:
            print("環境變數 'GEMINI_API_KEY' 未設定")
            self.api_key = None

    @commands.command()
    async def askai(self, ctx, *, prompt: str):
        if not self.api_key:
            await ctx.send("API 金鑰未配置，無法處理請求。")
            return
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            await ctx.send(response.text)
        except Exception as e:
            print(f"處理請求時發生錯誤：{e}")
            await ctx.send("抱歉，處理請求時出現錯誤，請稍後再試。")


async def setup(bot):
    await bot.add_cog(Ai(bot))
