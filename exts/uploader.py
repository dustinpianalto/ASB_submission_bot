import discord
from discord.ext import commands
from io import BytesIO
from .imports import process_files
from configparser import ConfigParser
import os

storage_dir = '../ASB_dino_submissions'


class Uploader:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='upload', aliases=['submit'])
    async def upload_dino(self, ctx, official: str='unofficial', singleplayer: bool=False):
        if ctx.message.attachments:
            attachment = ctx.message.attachements[0]
            if attachment.filename.endswith('.zip'):
                with BytesIO() as file:
                    await attachment.save(file)
                    unzipped = process_files.load_zip(file)
                    game_ini, dinos_data, mods = process_files.process_files(unzipped)
                    if dinos_data == dict():
                        await ctx.send('There aren\'t any DinoExport files in the zip file attached.\n'
                                       'Please make sure the files have not been renamed.')
                    else:
                        if official == 'unofficial' and game_ini == ConfigParser():
                            await ctx.send('Game.ini is missing or is not valid.')
                            return
                        elif official == 'official' and game_ini == ConfigParser():
                            if singleplayer:
                                game_ini.add_section('/script/shootergame.shootergamemode')
                                game_ini.set('/script/shootergame.shootergamemode', 'bUseSingleplayerSettings', True)
                        elif official not in ['official', 'unofficial']:
                            await ctx.send(f'{official} is not a valid option. Please specify "official" or '
                                           f'"unofficial" or leave it blank to default to "unofficial"')
                            return
                        if not os.path.isdir(f'{storage_dir}/{ctx.author.id}'):
                            os.mkdir(f'{storage_dir}/{ctx.author.id}')
                        directory = f'{storage_dir}/{ctx.author.id}/{attachment.filename}_' \
                                    f'{ctx.message.created_at.strftime("%Y%m%dT%H%M%S")}'
                        os.mkdir(directory)
                        process_files.generate_game_ini(game_ini, directory, mods)
                        process_files.generate_dino_files(dinos_data, directory)
                        await ctx.send('Upload complete.')
            else:
                await ctx.send('Please attach a zip file to the command.')
        else:
            await ctx.send('Please attach a zip file to the command.')


def setup(bot):
    bot.add_cog(Uploader(bot))
