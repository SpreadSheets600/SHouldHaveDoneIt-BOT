import os
import discord
import datetime
import streamlit as st
from KeepAlive import KeepAlive
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

load_dotenv()

st.write("ENV Variables Set : ", os.getenv("TOKEN") == st.secrets["TOKEN"])

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print("--------------------------------")
    print("----- + LOADED SHOULDUDU + -----")
    print("--------------------------------")

    await bot.change_presence(activity=discord.Game(name="With Codes"))

    bot.start_time = datetime.datetime.now()

    print("----- + LOADING COMMANDS + -----")
    print("--------------------------------")

    command_count = 0
    for command in bot.walk_application_commands():
        command_count += 1
        print(f"----- + Loaded : {command.name}")

    print("--------------------------------")
    print(f"---- + Loaded : {command_count} Commands + ----")
    print("--------------------------------")

    print("------- + LOADING COGS + -------")
    print(f"----- + Loaded : {len(bot.cogs)} Cogs + ------")
    print("--------------------------------")


@bot.slash_command(
    name="ping",
    description="Check Bot's Latency & Uptime",
)
async def ping(ctx: discord.ApplicationContext):
    latency = bot.latency * 1000
    uptime = datetime.datetime.now() - bot.start_time

    uptime_seconds = uptime.total_seconds()
    uptime_str = str(datetime.timedelta(seconds=uptime_seconds)).split(".")[0]

    embed = discord.Embed(
        title=":ping_pong: _*Pong !*_",
        description=f"Uptime : {uptime_str}\nLatency : {latency:.2f} ms",
        color=0x2F3136,
    )

    await ctx.respond(embed=embed)


@bot.slash_command(
    name="info",
    description="Get Bot Information",
)
async def info(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title=":information_source: Application Info",
        description="Multipurpose Discord Bot\nFor ShouldHaveDoneIt",
        color=0x2F3136,
    )

    embed.add_field(
        name="Links",
        value=":link: [ Terms ](https://spreadsheets600.me)\n:link: [ GitHub ](https://spreadsheets600.me)",
        inline=True,
    )

    embed.add_field(
        name="Developer",
        value=":gear: `SpreeadSheets600`",
        inline=False,
    )

    embed.add_field(
        name="Created At",
        value=f":calendar: `{bot.user.created_at.strftime('%Y-%m-%d %H:%M:%S')}`",
        inline=True,
    )

    embed.set_thumbnail(url=bot.user.avatar.url)
    await ctx.respond(embed=embed)


try:
    bot.load_extension("COGS.AI")
    bot.load_extension("COGS.GitHub")
    bot.load_extension("UTILS.CodeExecutor")
except Exception as e:
    print(f"An Error Occurred: {e}")

KeepAlive()
bot.run(os.getenv("TOKEN"))
