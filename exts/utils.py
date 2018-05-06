import discord
from discord.ext import commands
import math
import psutil


class Utils:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def ping(self, ctx):
        """Check the Bot\'s connection to Discord"""
        em = discord.Embed(style='rich',
                           title=f'Pong 🏓',
                           color=discord.Colour.green()
                           )
        msg = await ctx.send(embed=em)
        time1 = ctx.message.created_at
        time = (msg.created_at - time1).total_seconds() * 1000
        em.description = f'''Response Time: **{math.ceil(time)}ms**
        Discord Latency: **{math.ceil(self.bot.latency*1000)}ms**'''
        await msg.edit(embed=em)

    @commands.command(aliases=['oauth', 'link'])
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def invite(self, ctx, guy: discord.User=None):
        """Shows you the bot's invite link.
           If you pass in an ID of another bot, it gives you the invite link to that bot.
        """
        guy = guy or self.bot.user
        url = discord.utils.oauth_url(guy.id)
        await ctx.send(f'**{url}**')

    @commands.command()
    @commands.is_owner()
    async def sysinfo(self, ctx):
        await ctx.send(f'```ml\n'
                       f'CPU Percentages: {psutil.cpu_percent(percpu=True)}\n'
                       f'Memory Usage: {psutil.virtual_memory().percent}%\n'
                       f'Disc Usage: {psutil.disk_usage("/").percent}%\n'
                       f'```')


def setup(bot):
    bot.add_cog(Utils(bot))
