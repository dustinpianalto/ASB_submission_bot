import discord
from discord.ext import commands


class Uploader:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='submit', aliases=['upload'])
    async def upload_dino(self, ctx, official: str='unofficial'):
        if official == 'unofficial':
            pass


def setup(bot):
    bot.add_cog(Uploader(bot))
