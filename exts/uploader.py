import discord
from discord.ext import commands


class Uploader:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='submit', aliases=['upload'])
    async def upload_dino(self, ctx, official: str='unofficial'):
        if official == 'unofficial':
            pass
        elif official == 'official':
            pass
        else:
            await ctx.send(f'{official} is not a valid option. Please specify "official" or "unofficial" or leave it '
                           f'blank to default to "unofficial"')


def setup(bot):
    bot.add_cog(Uploader(bot))
