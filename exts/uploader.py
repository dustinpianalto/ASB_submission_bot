import discord
from discord.ext import commands
import zipfile
import os


class Uploader:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='submit', aliases=['upload'])
    async def upload_dino(self, ctx, official: str='unofficial'):
        if official == 'unofficial':

            with zipfile.ZipFile('archive.zip') as z:
                for filename in z.namelist():
                    if not os.path.isdir(filename):
                        with z.open(filename) as f:
                            for line in f:
                                print(line)


def setup(bot):
    bot.add_cog(Uploader(bot))
