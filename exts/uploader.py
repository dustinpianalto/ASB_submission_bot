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


import asyncio
import discord
from discord.ext import commands
from io import BytesIO
from .imports import process_files, utils
from configparser import ConfigParser
import os
from .imports.guid import Guid

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
                    if not os.path.isdir(f'{storage_dir}/orig/'):
                        os.mkdir(f'{storage_dir}/orig/')
                    with open(f'{storage_dir}/orig/{attachment.filename.replace(".zip", "")}_'
                              f'{ctx.message.created_at.strftime("%Y%m%dT%H%M%S")}.zip', 'wb') as file:
                        await attachment.save(file)
                    with BytesIO() as file:
                        await attachment.save(file)
                        unzipped = process_files.load_zip(file)
                        game_ini, dinos_data, mods, server_guid = process_files.process_files(unzipped)
                        if not game_ini and not dinos_data and not mods:
                            await msg.edit(content='There was an encoding error with one of the files provided '
                                                   'and they cannot be processed')
                            return
                        if dinos_data == dict():
                            await msg.edit(content='There aren\'t any DinoExport files in the zip file attached.\n'
                                           'Please make sure the files have not been renamed.')
                        else:
                            if official == 'unofficial' and game_ini == ConfigParser():
                                await msg.delete()
                                msg = await ctx.send(f'{ctx.author.mention} Game.ini is missing or is not valid.\n'
                                                     f'Select {self.bot.unicode_emojis["o"]} to process as Official\n'
                                                     f'Select {self.bot.unicode_emojis["y"]} if you would like to '
                                                     f'provide Game.ini separately.\n'
                                                     f'Select {self.bot.unicode_emojis["x"]} to cancel your upload\n'
                                                     f'Please wait until all reactions are loaded before making '
                                                     f'your selection')
                                await msg.add_reaction(self.bot.unicode_emojis["o"])
                                await msg.add_reaction(self.bot.unicode_emojis["y"])
                                await msg.add_reaction(self.bot.unicode_emojis["x"])

                                def echeck(reaction, user):
                                    return user == ctx.author and str(reaction.emoji) in [self.bot.unicode_emojis["o"],
                                                                                          self.bot.unicode_emojis["y"],
                                                                                          self.bot.unicode_emojis["x"]]

                                try:
                                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=echeck)
                                except asyncio.TimeoutError:
                                    await msg.edit(content=f'{ctx.author.mention} Game.ini is missing or not valid.\n'
                                                           f'Canceling request due to timeout.')
                                    return
                                else:
                                    try:
                                        await msg.clear_reactions()
                                    except (discord.Forbidden, discord.HTTPException):
                                        print('clear_reactions failed.')
                                        pass
                                    if str(reaction.emoji) == self.bot.unicode_emojis["o"]:
                                        await msg.edit(content="You chose to process as official.")
                                        await asyncio.sleep(4.0)
                                        official = 'official'
                                        server_guid = Guid(b'officialserver00')
                                    elif str(reaction.emoji) == self.bot.unicode_emojis["y"]:
                                        await msg.edit(content="You chose to provide the Game.ini file.\n"
                                                               "I will wait for 5 minutes for you to send a message "
                                                               "containing the word `game` with a single file attached "
                                                               "named `Game.ini`")

                                        def mcheck(m):
                                            return 'game' in m.content.lower() and \
                                                   m.channel == ctx.channel and \
                                                   m.author == ctx.author and \
                                                   len(m.attachments) > 0 and \
                                                   m.attachments[0].filename == 'Game.ini'

                                        try:
                                            game_msg = await self.bot.wait_for('message', timeout=300.0, check=mcheck)
                                        except asyncio.TimeoutError:
                                            await msg.edit(content=f'{ctx.author.mention} Timeout reached.\n'
                                                                   f'Your request has been canceled.')
                                            return
                                        else:
                                            await msg.edit(content='File Received.')
                                            await asyncio.sleep(2)
                                            await msg.edit(content='Processing... Please Wait.')
                                            with BytesIO() as f:
                                                game_msg.attachments[0].save(f)
                                                game_ini = process_files.process_file(f, 'game.ini')
                                                f.seek(0)
                                                server_guid = process_files.get_server_guid(f.read())
                                    elif str(reaction.emoji) == self.bot.unicode_emojis['x']:
                                        await msg.edit(content='Your request has been canceled.')
                                        return

                            if official == 'official' and game_ini == ConfigParser():
                                if not singleplayer:
                                    await msg.delete()
                                    msg = await ctx.send(f'Is this from SinglePlayer or a server?\n'
                                                         f"select {self.bot.unicode_emojis['y']} for SP or "
                                                         f"{self.bot.unicode_emojis['x']} for server.")
                                    await msg.add_reaction(self.bot.unicode_emojis["y"])
                                    await msg.add_reaction(self.bot.unicode_emojis["x"])

                                    def echeck(reaction, user):
                                        return user == ctx.author and str(reaction.emoji) \
                                               in [self.bot.unicode_emojis["y"], self.bot.unicode_emojis["x"]]

                                    try:
                                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0,
                                                                                 check=echeck)
                                    except asyncio.TimeoutError:
                                        await msg.edit(
                                            content=f'{ctx.author.mention} Game.ini is missing or not valid.\n'
                                                    f'Canceling request due to timeout.')
                                        return
                                    else:
                                        try:
                                            await msg.clear_reactions()
                                        except (discord.Forbidden, discord.HTTPException):
                                            print('clear_reactions failed.')
                                            pass
                                        if str(reaction.emoji) == self.bot.unicode_emojis["y"]:
                                            await msg.edit(content="You selected SinglePlayer.")
                                            await asyncio.sleep(4.0)
                                            singleplayer = True
                                            server_guid = Guid(b'officialsinglepl')
                                        elif str(reaction.emoji) == self.bot.unicode_emojis["x"]:
                                            await msg.edit(content="You selected Server.")
                                            await asyncio.sleep(4.0)
                                            singleplayer = False
                                            server_guid = Guid(b'officialserver00')

                                if singleplayer:
                                    game_ini.add_section('/script/shootergame.shootergamemode')
                                    game_ini.set('/script/shootergame.shootergamemode',
                                                 'bUseSingleplayerSettings',
                                                 "True")

                            if official not in ['official', 'unofficial']:
                                await msg.edit(content=f'{ctx.author.mention} {official} is not a valid option.\n'
                                                       f'Please specify "official" or "unofficial" or leave it blank '
                                                       f'to default to "unofficial"')
                                return

                            await msg.edit(content='Processing... Syncing with GitHub')
                            pull_status = await utils.git_pull(self.bot.loop, storage_dir)
                            if pull_status == 'Completed':
                                await msg.edit(content='Processing... Sync complete... Generating new files')
                                process_files.generate_files(storage_dir, ctx, server_guid,
                                                             game_ini, dinos_data, mods)
                                await msg.edit(content='Processing... Files generated... Committing changes')
                                await utils.git_add(self.bot.loop, storage_dir, '*')
                                if await utils.git_commit(self.bot.loop,
                                                          storage_dir,
                                                          f'"Uploaded {len(dinos_data)} dinos {official}"'):
                                    await msg.edit(content='Processing... Committed... Pushing files to GitHub')
                                    push_status = await utils.git_push(self.bot.loop, storage_dir)
                                    if push_status == 'Completed':
                                        await msg.delete()
                                        msg = await ctx.send(f'{ctx.author.mention} Upload complete.\n'
                                                             f'Uploaded {len(dinos_data)} dinos as {official} '
                                                             f'{"singleplayer" if singleplayer else "server"}')
                                    else:
                                        await self.bot.get_user(owner_id).send(f'There was an error with git push'
                                                                               f'\n{push_status}')
                                        await msg.edit(content='There was an error pushing the files to GitHub\n'
                                                               'Dusty.P has been notified and will get this fixed')
                                else:
                                    await self.bot.get_user(owner_id).send(f'There was an error with git commit')
                                    await msg.edit(content='There was an error committing the files\n'
                                                           'Dusty.P has been notified and will get this fixed')
                            else:
                                await self.bot.get_user(owner_id).send(f'There was an error with git pull\n'
                                                                       f'{pull_status}')
                                process_files.generate_files('submissions_temp', ctx, server_guid,
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
