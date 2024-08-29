from discord.ext import commands
import random



class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def games(self, ctx , *args):
        game_list = list(args)
        await ctx.send(random.choice(game_list))
    
async def setup(bot):
    await bot.add_cog(Dice(bot))