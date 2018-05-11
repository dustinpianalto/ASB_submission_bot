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
import logging
import json
import aiohttp
import asyncpg
from concurrent import futures
from typing import Dict
from datetime import datetime

log_format = '{asctime}.{msecs:03.0f}|{levelname:<8}|{name}::{message}'
date_format = '%Y.%m.%d %H.%M.%S'

log_dir = 'logs'

log_file = '{0}/submitter_{1}.log'.format(log_dir, datetime.now().strftime('%Y%m%d_%H%M%S%f'))

logging.basicConfig(level=logging.DEBUG, style='{', filename=log_file, datefmt=date_format, format=log_format)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(log_format, style='{', datefmt=date_format)
console_handler.setFormatter(formatter)
logging.getLogger('').addHandler(console_handler)

extension_dir = 'exts'
owner_id = 351794468870946827
bot_config_file = 'bot_config.json'
secrets_file = 'bot_secrets.json'
config_dir = 'config/'

description = 'Submission Bot for Ark Smart Breeder'


class Submitter(commands.Bot):
    def __init__(self, **kwargs):
        kwargs["command_prefix"] = self.get_custom_prefix
        super().__init__(**kwargs)
        self.aio_session = aiohttp.ClientSession(loop=self.loop)
        with open(f'{config_dir}{bot_config_file}') as file:
            self.bot_config = json.load(file)
        with open(f'{config_dir}{secrets_file}') as file:
            self.bot_secrets = json.load(file)
        self.guild_config = {}
        self.infected = {}
        self.TOKEN = self.bot_secrets['token']
        del self.bot_secrets['token']
        self.db_con = None
        self.default_prefix = '!'
        self.tpe = futures.ThreadPoolExecutor()
        self.embed_color = discord.Colour.from_rgb(49, 107, 111)
        self.unicode_emojis: Dict[str, str] = {
                                        'x': '❌',
                                        'y': '✅',
                                        'poop': '💩',
                                        'boom': '💥',
                                        'left_fist': '🤛',
                                        'o': '🇴',
                                        }

    async def connect_db(self):
        self.db_con = await asyncpg.create_pool(host=self.bot_secrets['db_con']['host'],
                                                database=self.bot_secrets['db_con']['db_name'],
                                                user=self.bot_secrets['db_con']['user'],
                                                password=self.bot_secrets['db_con']['password'],
                                                loop=self.loop)

    @staticmethod
    async def get_custom_prefix(bot_inst, message):
        return await bot_inst.db_con.fetchval('select prefix from guild_config where guild_id = $1',
                                              message.guild.id) or bot_inst.default_prefix

    async def load_ext(self, ctx, mod=None):
        self.load_extension('{0}.{1}'.format(extension_dir, mod))
        if ctx is not None:
            await ctx.send('{0} loaded.'.format(mod))

    async def unload_ext(self, ctx, mod=None):
        self.unload_extension('{0}.{1}'.format(extension_dir, mod))
        if ctx is not None:
            await ctx.send('{0} unloaded.'.format(mod))

    async def close(self):
        await super().close()
        await self.aio_session.close()


bot = Submitter(description=description, case_insensitive=True)


@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, mod=None):
    """Allows the owner to load extensions dynamically"""
    await bot.load_ext(ctx, mod)


@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, mod=None):
    """Allows the owner to reload extensions dynamically"""
    if mod == 'all':
        load_list = bot.bot_config['load_list']
        for load_item in load_list:
            await bot.unload_ext(ctx, f'{load_item}')
            await bot.load_ext(ctx, f'{load_item}')
    else:
        await bot.unload_ext(ctx, mod)
        await bot.load_ext(ctx, mod)


@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, mod):
    """Allows the owner to unload extensions dynamically"""
    await bot.unload_ext(ctx, mod)


@bot.event
async def on_message(ctx):
    if not ctx.author.bot:
        if ctx.guild:
            if int(await bot.db_con.fetchval("select channel_lockdown from guild_config where guild_id = $1",
                                             ctx.guild.id)):
                if ctx.channel.id in json.loads(await bot.db_con.fetchval("select allowed_channels from guild_config "
                                                                          "where guild_id = $1",
                                                                          ctx.guild.id)):
                    await bot.process_commands(ctx)
            else:
                await bot.process_commands(ctx)
        else:
            await bot.process_commands(ctx)


@bot.event
async def on_ready():
    if bot.db_con is None:
        await bot.connect_db()
    bot.recent_msgs = {}
    logging.info('Logged in as {0.name}|{0.id}'.format(bot.user))
    load_list = bot.bot_config['load_list']
    for load_item in load_list:
        await bot.load_ext(None, f'{load_item}')
        logging.info('Extension Loaded: {0}'.format(load_item))
    with open(f'{config_dir}reboot', 'r') as f:
        reboot = f.readlines()
    if int(reboot[0]) == 1:
        await bot.get_channel(int(reboot[1])).send('Restart Finished.')
    with open(f'{config_dir}reboot', 'w') as f:
        f.write(f'0')
    logging.info('Done loading, Submitter is active.')

bot.run(bot.TOKEN)
