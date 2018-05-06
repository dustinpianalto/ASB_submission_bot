import discord
from discord.ext import commands
import os
from .imports import checks, utils
import json
import logging

admin_log = logging.getLogger('admin')
config_dir = 'config/'
bot_config_file = 'bot_config.json'


class Admin:
    def __init__(self, bot):
        self.bot = bot

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
        config = self.bot.con.one('select * from guild_config where guild_id = %(id)s', {'id': ctx.guild.id})
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
                    if self.bot.con.one('select allowed_channels from guild_config where guild_id = %(id)s',
                                        {'id': ctx.guild.id}) is []:
                        await ctx.send('Please set at least one allowed channel before running this command.')
                    else:
                        self.bot.con.run('update guild_config set channel_lockdown = True where guild_id = %(id)s',
                                         {'id': ctx.guild.id})
                        await ctx.send('Channel Lockdown is now active.')
                elif str(config).lower() == 'false':
                    if self.bot.con.one('select channel_lockdown from guild_config where guild_id = %(id)s',
                                        {'id': ctx.guild.id}):
                        self.bot.con.run('update guild_config set channel_lockdown = False where guild_id = %(id)s',
                                         {'id': ctx.guild.id})
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
                        if self.bot.con.one('select allowed_channels from guild_config where guild_id = %(id)s',
                                            {'id': ctx.guild.id}):
                            if chnl.id in json.loads(self.bot.con.one('select allowed_channels from guild_config '
                                                                      'where guild_id = %(id)s',
                                                                      {'id': ctx.guild.id})):
                                admin_log.info('Chan found in config')
                                await ctx.send(f'{channel} is already in the list of allowed channels. Skipping...')
                            else:
                                admin_log.info('Chan not found in config')
                                allowed_channels = json.loads(self.bot.con.one('select allowed_channels from '
                                                                               'guild_config where guild_id = %(id)s',
                                                                               {'id': ctx.guild.id})).append(chnl.id)
                                self.bot.con.run('update guild_config set allowed_channels = %(channels)s '
                                                 'where guild_id = %(id)s',
                                                 {'id': ctx.guild.id, 'channels': allowed_channels})
                                added = f'{added}\n{channel}'
                        else:
                            admin_log.info('Chan not found in config')
                            allowed_channels = [chnl.id]
                            self.bot.con.run('update guild_config set allowed_channels = %(channels)s '
                                             'where guild_id = %(id)s',
                                             {'id': ctx.guild.id, 'channels': allowed_channels})
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


def setup(bot):
    bot.add_cog(Admin(bot))
