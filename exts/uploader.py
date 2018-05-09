import discord
from discord.ext import commands
from io import BytesIO
from .imports import process_files, utils
from configparser import ConfigParser
import os

storage_dir = '../ASB_dino_submissions'
owner_id = 351794468870946827


class Uploader:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='upload', aliases=['submit'])
    async def upload_dino(self, ctx, official: str='unofficial', singleplayer: bool=False):
        msg = await ctx.send('Processing... Please Wait')
        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            if attachment.filename.endswith('.zip'):
                async with ctx.typing():
                    with BytesIO() as file:
                        await attachment.save(file)
                        unzipped = process_files.load_zip(file)
                        game_ini, dinos_data, mods = process_files.process_files(unzipped)
                        if not game_ini and not dinos_data and not mods:
                            await msg.edit(content='There was an encoding error with one of the files provided'
                                                   'and they cannot be processed')
                            return
                        if dinos_data == dict():
                            await msg.edit(content='There aren\'t any DinoExport files in the zip file attached.\n'
                                           'Please make sure the files have not been renamed.')
                        else:
                            if official == 'unofficial' and game_ini == ConfigParser():
                                await msg.edit(content='Game.ini is missing or is not valid.')
                                return
                            elif official == 'official' and game_ini == ConfigParser():
                                if singleplayer:
                                    game_ini.add_section('/script/shootergame.shootergamemode')
                                    game_ini.set('/script/shootergame.shootergamemode',
                                                 'bUseSingleplayerSettings',
                                                 True)
                            elif official not in ['official', 'unofficial']:
                                await msg.edit(content=f'{official} is not a valid option. Please specify "official" '
                                                       f'or "unofficial" or leave it blank to default to "unofficial"')
                                return
                            await msg.edit(content='Processing... Syncing with GitHub')
                            pull_status = await utils.git_pull(self.bot.loop, storage_dir)
                            if pull_status == 'Completed':
                                await msg.edit(content='Processing... Sync complete... Generating new files')
                                process_files.generate_files(storage_dir, ctx, attachment.filename,
                                                             game_ini, dinos_data, mods)
                                await msg.edit(content='Processing... Files generated... Committing changes')
                                await utils.git_add(self.bot.loop, storage_dir, '*')
                                if await utils.git_commit(self.bot.loop,
                                                          storage_dir,
                                                          f'"Uploaded {len(dinos_data)} dinos {official}"'):
                                    await msg.edit(content='Processing... Committed... Pushing files to GitHub')
                                    push_status = await utils.git_push(self.bot.loop, storage_dir)
                                    if push_status == 'Completed':
                                        await msg.edit(content=f'{ctx.author.mention} Upload complete.')
                                    else:
                                        await self.bot.get_user(owner_id).send(f'There was an error with git push'
                                                                               f'\n{push_status}')
                                        await msg.edit(content='There was an error pushing the files to GitHub\n'
                                                               'Dusty.P has been notified and will get this fixed')
                                else:
                                    await msg.edit(content='There was an error committing the files\n'
                                                           'Dusty.P has been notified and will get this fixed')
                            else:
                                await self.bot.get_user(owner_id).send(f'There was an error with git pull\n'
                                                                       f'{pull_status}')
                                process_files.generate_files('submissions_temp', ctx, attachment.filename,
                                                             game_ini, dinos_data, mods)
                                await msg.edit(content='Could not sync with GitHub.\n'
                                                       'Dusty.P has been notified and your files are stored in a '
                                                       'temporary location')
            else:
                await msg.edit(content='Please attach a zip file to the command.')
        else:
            await msg.edit(content='Please attach a zip file to the command.')


def setup(bot):
    bot.add_cog(Uploader(bot))
