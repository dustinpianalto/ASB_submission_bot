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
from .imports import checks, utils
import json
import logging
import inspect
import os

admin_log = logging.getLogger('admin')
config_dir = 'config/'
bot_config_file = 'bot_config.json'


class Admin:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reboot(self, ctx):
        await ctx.send('Submitter is restarting.')
        with open(f'{config_dir}reboot', 'w') as f:
            f.write(f'1\n{ctx.channel.id}')
        os._exit(1)

    @commands.group(case_insensitive=True)
    async def set(self, ctx):
        """Run help set for more info"""
        pass

    @commands.group(case_insensitive=True)
    async def add(self, ctx):
        """Run help set for more info"""
        pass

    @commands.group(case_insensitive=True)
    async def remove(self, ctx):
        """Run help set for more info"""
        pass

    @commands.command(hidden=True)
    @commands.check(checks.is_guild_owner)
    async def get_guild_config(self, ctx):
        config = await self.bot.db_con.fetchval('select * from guild_config where guild_id = $1', ctx.guild.id)
        configs = [str(config)[i:i+1990] for i in range(0, len(config), 1990)]
        await ctx.message.author.send(f'The current config for the {ctx.guild.name} guild is:\n')
        admin_log.info(configs)
        for config in configs:
            await ctx.message.author.send(f'```{config}```')
        await ctx.send(f'{ctx.message.author.mention} check your DMs.')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def get_bot_config(self, ctx):
        n = 2000
        config = [str(self.bot.bot_config)[i:i+n] for i in range(0, len(str(self.bot.bot_config)), n)]
        for conf in config:
            await ctx.message.author.send(conf)
        await ctx.send(f'{ctx.message.author.mention} check your DMs.')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload_bot_config(self, ctx):
        with open(f'{config_dir}{bot_config_file}') as file:
            self.bot.bot_config = json.load(file)
        del self.bot.bot_config['token']
        del self.bot.bot_config['db_con']
        await ctx.send('Config reloaded.')

    @set.command(name='channel_lockdown', aliases=['lockdown', 'restrict_access', 'cl'])
    async def _channel_lockdown(self, ctx, config='true'):
        if ctx.guild:
            if checks.is_admin(self.bot, ctx):
                if str(config).lower() == 'true':
                    if await self.bot.db_con.fetchval('select allowed_channels from guild_config '
                                                      'where guild_id = $1', ctx.guild.id) is []:
                        await ctx.send('Please set at least one allowed channel before running this command.')
                    else:
                        await self.bot.db_con.execute('update guild_config set channel_lockdown = True '
                                                      'where guild_id = $1', ctx.guild.id)
                        await ctx.send('Channel Lockdown is now active.')
                elif str(config).lower() == 'false':
                    if await self.bot.db_con.fetchval('select channel_lockdown from guild_config '
                                                      'where guild_id = $1', ctx.guild.id):
                        await self.bot.db_con.execute('update guild_config set channel_lockdown = False '
                                                      'where guild_id = $1', ctx.guild.id)
                        await ctx.send('Channel Lockdown has been deactivated.')
                    else:
                        await ctx.send('Channel Lockdown is already deactivated.')
            else:
                await ctx.send(f'You are not authorized to run this command.')
        else:
            await ctx.send('This command must be run from inside a guild.')

    @add.command(name='allowed_channels', aliases=['channel', 'ac'])
    async def _allowed_channels(self, ctx, *, channels):
        if ctx.guild:
            if checks.is_admin(self.bot, ctx):
                channels = channels.lower().replace(' ', '').split(',')
                added = ''
                for channel in channels:
                    chnl = discord.utils.get(ctx.guild.channels, name=channel)
                    if chnl is None:
                        await ctx.send(f'{channel} is not a valid text channel in this guild.')
                    else:
                        admin_log.info('Chan found')
                        if await self.bot.db_con.fetchval('select allowed_channels from guild_config '
                                                          'where guild_id = $1', ctx.guild.id):
                            if chnl.id in await  self.bot.con.fetchval('select allowed_channels from guild_config '
                                                                       'where guild_id = $1',
                                                                       ctx.guild.id):
                                admin_log.info('Chan found in config')
                                await ctx.send(f'{channel} is already in the list of allowed channels. Skipping...')
                            else:
                                admin_log.info('Chan not found in config')
                                allowed_channels = await self.bot.db_con.fetchval('select allowed_channels from '
                                                                                  'guild_config where guild_id = $1',
                                                                                  ctx.guild.id).append(chnl.id)
                                await self.bot.db_con.execute('update guild_config set allowed_channels = $2 '
                                                              'where guild_id = $1',
                                                              ctx.guild.id, allowed_channels)
                                added = f'{added}\n{channel}'
                        else:
                            admin_log.info('Chan not found in config')
                            allowed_channels = [chnl.id]
                            await self.bot.db_con.execute('update guild_config set allowed_channels = $2 '
                                                          'where guild_id = $1',
                                                          ctx.guild.id, allowed_channels)
                            added = f'{added}\n{channel}'
                if added != '':
                    await ctx.send(f'The following channels have been added to the allowed channel list: {added}')
                await ctx.message.add_reaction('✅')
            else:
                await ctx.send(f'You are not authorized to run this command.')
        else:
            await ctx.send('This command must be run from inside a guild.')

    @commands.command()
    @commands.is_owner()
    async def view_code(self, ctx, code_name):
        pages = utils.paginate(inspect.getsource(self.bot.get_command(code_name).callback))
        for page in pages:
            await ctx.send(page)

    @add.command(name='admin_role', aliases=['admin'])
    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    @commands.check(checks.is_guild_owner)
    async def _add_admin_role(self, ctx, role=None):
        role = discord.utils.get(ctx.guild.roles, name=role)
        if role is not None:
            roles = await self.bot.db_con.fetchval('select admin_roles from guild_config where guild_id = $1',
                                                   ctx.guild.id)
            if role.id in roles:
                await ctx.send(f'{role.name} is already registered as an admin role in this guild.')
            else:
                roles.append(role.id)
                await self.bot.db_con.execute('update guild_config set admin_roles = $2 where guild_id = $1',
                                              ctx.guild.id, roles)
                await ctx.send(f'{role.name} has been added to the list of admin roles for this guild.')
        else:
            await ctx.send('You must include a valid role name with this command.')

    @remove.command(name='admin_role', aliases=['admin'])
    @commands.cooldown(1, 5, type=commands.BucketType.guild)
    @commands.check(checks.is_guild_owner)
    async def _remove_admin_role(self, ctx, role=None):
        role = discord.utils.get(ctx.guild.roles, name=role)
        if role is not None:
            roles = await self.bot.db_con.fetchval('select admin_roles from guild_config where guild_id = $1',
                                                   ctx.guild.id)
            if role.id in roles:
                roles.remove(role.id)
                await self.bot.db_con.execute('update guild_config set admin_roles = $2 where guild_id = $1',
                                              ctx.guild.id, roles)
                await ctx.send(f'{role.name} has been removed from the list of admin roles for this guild.')
            else:
                await ctx.send(f'{role.name} is not registered as an admin role in this guild.')
        else:
            await ctx.send('You must include a valid role name with this command.')


def setup(bot):
    bot.add_cog(Admin(bot))
