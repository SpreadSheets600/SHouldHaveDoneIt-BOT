import os
import json
import aiohttp
import discord
import streamlit as st
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

st.write(
    "ENV Variables Set : ",
    os.environ["JDOODLE_CLIENT_ID"] == st.secrets["JDOODLE_CLIENT_ID"],
)
st.write(
    "ENV Variables Set : ",
    os.environ["JDOODLE_CLIENT_SECRET"] == st.secrets["JDOODLE_CLIENT_SECRET"],
)


class CodeExecution(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jdoodle_url = "https://api.jdoodle.com/v1/execute"
        self.client_id = os.getenv("JDOODLE_CLIENT_ID")
        self.client_secret = os.getenv("JDOODLE_CLIENT_SECRET")

    @commands.slash_command(name="execute")
    async def execute_code(self, ctx, language: str, *, code: str):

        language_map = {
            "python": ("python3", "3"),
            "java": ("java", "4"),
            "cpp": ("cpp", "5"),
            "c": ("c", "5"),
            "js": ("nodejs", "4"),
        }

        if language.lower() not in language_map:
            await ctx.send(
                f"Unsupported Language! Supported Languages: {', '.join(language_map.keys())}"
            )
            return

        selected_lang, version_index = language_map[language.lower()]

        payload = {
            "script": code,
            "language": selected_lang,
            "versionIndex": version_index,
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.jdoodle_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    output = result.get("output", "No output")
                    memory = result.get("memory", "N/A")
                    cpu_time = result.get("cpuTime", "N/A")

                    embed = discord.Embed(
                        title=f"Code Execution - {language.capitalize()}",
                        color=discord.Color.green(),
                    )
                    embed.add_field(
                        name="Code", value=f"```{language}\n{code}```", inline=False
                    )
                    embed.add_field(
                        name="Output", value=f"```{output}```", inline=False
                    )
                    embed.set_footer(text=f"Memory: {memory} | CPU Time: {cpu_time}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Error executing the code. Please try again later.")


def setup(bot):
    bot.add_cog(CodeExecution(bot))
