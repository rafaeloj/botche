import discord
from discord.ext import commands, tasks
from cogs.table import TableCog
import asyncio
import os
import json

class Botche(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print('--------')

    @tasks.loop(seconds=10) 
    async def change_presence(self):
        print("OI")

    @commands.command()
    async def info(self, ctx):
        print(ctx.channel.id)
        await ctx.send("Remember, to find the conference's qualis it used https://ppgcc.github.io/discentesPPGCC/ and  http://www.wikicfp.com/cfp/ through a levenshtein distance. So how bigger is similarity mean that qualis is probabilly wrong WikiCFP")



with open('config.json') as f:
    config = json.load(f)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or(config['trigger']), description="Bigode grosso e facão na mão!", intents=intents)

@bot.event
async def on_ready():
    print("To com chimarrão na mão!")

async def main():
    await bot.add_cog(Botche(bot))
    await bot.add_cog(TableCog(bot, config['table']['path'], config['table']['keys_path'], config['warning']['channel'], config['warning']['deadline']))
    await bot.start(os.environ["BOTCHE_TOKEN"])

if __name__ =="__main__":
    asyncio.run(main())