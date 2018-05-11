"""
===

MIT License

Copyright (c) 2018 Dusty.P https://github.com/dustinpianalto

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""


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
        em.description = f'Response Time: **{math.ceil(time)}ms**\n' \
                         f'Discord Latency: **{math.ceil(self.bot.latency*1000)}ms**'
        await msg.edit(embed=em)

    @commands.command(aliases=['oauth', 'link'])
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def invite(self, ctx, guy: discord.User=None):
        """Shows you the bot's invite link.
           If you pass in an ID of another bot, it gives you the invite link to that bot.
        """
        guy = guy or self.bot.user
        url = discord.utils.oauth_url(guy.id)
        await ctx.send(f'**<{url}>**')

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
