import time
import discord
import aiohttp
from datetime import datetime
from discord.ext import commands
from discord import SlashCommandGroup


def iso_unix_timestamp(iso: str):
    try:
        dt = datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")
        uix = int(time.mktime(dt.timetuple()))
        return uix
    except ValueError as e:
        print(f"Error parsing date: {e}")


class GitHub(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    github = SlashCommandGroup(name="github", description="GitHub Commands")
    info = github.create_subgroup(
        name="info", description="Get Information About A GitHub Repository"
    )

    @github.command(name="user", description="Get Information About A GitHub User")
    async def user(self, ctx, user: str):
        await ctx.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.github.com/users/{user}") as response:
                if response.status != 200:
                    await ctx.followup.send(
                        f"Error Fetching User Data: {response.status}"
                    )
                    return

                data = await response.json()

        embed = discord.Embed(
            title=f"{data.get("name", user)}",
            description=f"{data.get("bio", 'No bio available.')}\n### Location : {data['location']}\n",
            color=discord.Color.blue(),
            url=data.get("html_url", ""),
        )

        embed.set_author(
            name=f"Username : {data.get("login", user)}",
            icon_url=data.get("avatar_url", ""),
        )

        embed.add_field(
            name="🍴 Repositories",
            value=data.get("public_repos", 0),
            inline=True,
        )
        embed.add_field(
            name="⭐ Followers", value=data.get("followers", 0), inline=True
        )
        embed.add_field(
            name="👀 Following", value=data.get("following", 0), inline=True
        )

        created_at = data.get("created_at", None)
        updated_at = data.get("updated_at", None)

        if created_at:
            embed.add_field(
                name="🕒 Created At",
                value=f"<t:{iso_unix_timestamp(created_at)}:R>",
                inline=True,
            )
        else:
            embed.add_field(name="🕒 Created At", value="Unknown", inline=True)

        if updated_at:
            embed.add_field(
                name="🕒 Updated At",
                value=f"<t:{iso_unix_timestamp(updated_at)}:R>",
                inline=True,
            )
        else:
            embed.add_field(name="🕒 Updated At", value="Unknown", inline=True)

        if data["blog"]:
            if data["blog"].startswith("http"):
                blog = data["blog"]
            else:
                blog = "https://" + data["blog"]
        else:
            blog = None

        if data["twitter_username"]:
            twitter = "www.x.com/" + data["twitter_username"]
        else:
            twitter = None

        view = ProfileLinks(blog=blog, twitter=twitter)
        await ctx.followup.send(embed=embed, view=view)

    @github.command(
        name="repo", description="Get Information About A GitHub Repository"
    )
    async def repo(self, ctx, repo: str):
        await ctx.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.github.com/repos/{repo}") as response:
                if response.status != 200:
                    await ctx.followup.send(
                        f"Error Fetching Repository Data: {response.status}\n\nThe Format Should Be: `Owner/Repository`"
                    )
                    return

                data = await response.json()

        embed = discord.Embed(
            title=f"{data.get("full_name", "Unknown")}",
            description=f"{data.get("description", "No description available.")}\n### Language : {data['language']}\n",
            color=discord.Color.blue(),
            url=data.get("html_url", ""),
        )

        embed.set_author(
            name=f"Created By : {data.get("owner", {}).get("login", "Unknown")}",
            icon_url=data.get("owner", {}).get("avatar_url", ""),
        )

        embed.add_field(name="🍴 Forks", value=data.get("forks_count", 0), inline=True)
        embed.add_field(
            name="⭐ Stars", value=data.get("stargazers_count", 0), inline=True
        )
        embed.add_field(
            name="👀 Watchers", value=data.get("watchers_count", 0), inline=True
        )
        embed.add_field(
            name="📝 Open Issues", value=data.get("open_issues_count", 0), inline=True
        )

        created_at = data.get("created_at", None)
        updated_at = data.get("updated_at", None)

        if created_at:
            embed.add_field(
                name="🕒 Created At",
                value=f"<t:{iso_unix_timestamp(created_at)}:R>",
                inline=True,
            )
        else:
            embed.add_field(name="🕒 Created At", value="Unknown", inline=True)

        if updated_at:
            embed.add_field(
                name="🕒 Updated At",
                value=f"<t:{iso_unix_timestamp(updated_at)}:R>",
                inline=True,
            )
        else:
            embed.add_field(name="🕒 Updated At", value="Unknown", inline=True)

        topics = data.get("topics", [])
        if topics:
            embed.add_field(name="🔗 Topics", value=", ".join(topics), inline=False)
        else:
            embed.add_field(
                name="🔗 Topics",
                value="No topics available.",
            )

    @info.command(name="yars", description="Get Information About YARS")
    async def yars(self, ctx):
        await ctx.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/repos/datavorous/yars"
            ) as response:
                if response.status != 200:
                    await ctx.followup.send(
                        f"Error fetching repository data: {response.status}"
                    )
                    return

                data = await response.json()

        embed = discord.Embed(
            title="YARS Repository Information",
            description=f"{data.get("description", "No description available.")}\n### Language : {data['language']}\n",
            color=discord.Color.blue(),
            url=data.get("html_url", ""),
        )

        embed.set_author(
            name=f"Created By : {data.get("owner", {}).get("login", "Unknown")}",
            icon_url=data.get("owner", {}).get("avatar_url", ""),
        )

        embed.add_field(name="🍴 Forks", value=data.get("forks_count", 0), inline=True)
        embed.add_field(
            name="⭐ Stars", value=data.get("stargazers_count", 0), inline=True
        )
        embed.add_field(
            name="👀 Watchers", value=data.get("watchers_count", 0), inline=True
        )
        embed.add_field(
            name="📝 Open Issues", value=data.get("open_issues_count", 0), inline=True
        )

        created_at = data.get("created_at", None)
        updated_at = data.get("updated_at", None)

        if created_at:
            embed.add_field(
                name="🕒 Created At",
                value=f"<t:{iso_unix_timestamp(created_at)}:R>",
                inline=True,
            )
        else:
            embed.add_field(name="🕒 Created At", value="Unknown", inline=True)

        if updated_at:
            embed.add_field(
                name="🕒 Updated At",
                value=f"<t:{iso_unix_timestamp(updated_at)}:R>",
                inline=True,
            )
        else:
            embed.add_field(name="🕒 Updated At", value="Unknown", inline=True)

        topics = data.get("topics", [])
        if topics:
            embed.add_field(name="🔗 Topics", value=", ".join(topics), inline=False)
        else:
            embed.add_field(
                name="🔗 Topics", value="No topics available.", inline=False
            )

        await ctx.followup.send(embed=embed)

    @info.command(name="amine", description="Get Information About AMINE")
    async def yars(self, ctx):
        await ctx.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/repos/datavorous/amine"
            ) as response:
                if response.status != 200:
                    await ctx.followup.send(
                        f"Error fetching repository data: {response.status}"
                    )
                    return

                data = await response.json()

        embed = discord.Embed(
            title="YARS Repository Information",
            description=f"{data.get("description", "No description available.")}\n### Language : {data['language']}\n",
            color=discord.Color.blue(),
            url=data.get("html_url", ""),
        )

        embed.set_author(
            name=f"Created By : {data.get("owner", {}).get("login", "Unknown")}",
            icon_url=data.get("owner", {}).get("avatar_url", ""),
        )

        embed.add_field(name="🍴 Forks", value=data.get("forks_count", 0), inline=True)
        embed.add_field(
            name="⭐ Stars", value=data.get("stargazers_count", 0), inline=True
        )
        embed.add_field(
            name="👀 Watchers", value=data.get("watchers_count", 0), inline=True
        )
        embed.add_field(
            name="📝 Open Issues", value=data.get("open_issues_count", 0), inline=True
        )

        created_at = data.get("created_at", None)
        updated_at = data.get("updated_at", None)

        if created_at:
            embed.add_field(
                name="🕒 Created At",
                value=f"<t:{iso_unix_timestamp(created_at)}:R>",
                inline=True,
            )
        else:
            embed.add_field(name="🕒 Created At", value="Unknown", inline=True)

        if updated_at:
            embed.add_field(
                name="🕒 Updated At",
                value=f"<t:{iso_unix_timestamp(updated_at)}:R>",
                inline=True,
            )
        else:
            embed.add_field(name="🕒 Updated At", value="Unknown", inline=True)

        topics = data.get("topics", [])
        if topics:
            embed.add_field(name="🔗 Topics", value=", ".join(topics), inline=False)
        else:
            embed.add_field(
                name="🔗 Topics", value="No topics available.", inline=False
            )

        await ctx.followup.send(embed=embed)

    @info.command(name="doubtnutx", description="Get Information About DoubtnutX")
    async def yars(self, ctx):
        await ctx.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/repos/datavorous/DoubtnutPremiumPass"
            ) as response:
                if response.status != 200:
                    await ctx.followup.send(
                        f"Error fetching repository data: {response.status}"
                    )
                    return

                data = await response.json()

        embed = discord.Embed(
            title="YARS Repository Information",
            description=f"{data.get("description", "No description available.")}\n### Language : {data['language']}\n",
            color=discord.Color.blue(),
            url=data.get("html_url", ""),
        )

        embed.set_author(
            name=f"Created By : {data.get("owner", {}).get("login", "Unknown")}",
            icon_url=data.get("owner", {}).get("avatar_url", ""),
        )

        embed.add_field(name="🍴 Forks", value=data.get("forks_count", 0), inline=True)
        embed.add_field(
            name="⭐ Stars", value=data.get("stargazers_count", 0), inline=True
        )
        embed.add_field(
            name="👀 Watchers", value=data.get("watchers_count", 0), inline=True
        )
        embed.add_field(
            name="📝 Open Issues", value=data.get("open_issues_count", 0), inline=True
        )

        created_at = data.get("created_at", None)
        updated_at = data.get("updated_at", None)

        if created_at:
            embed.add_field(
                name="🕒 Created At",
                value=f"<t:{iso_unix_timestamp(created_at)}:R>",
                inline=True,
            )
        else:
            embed.add_field(name="🕒 Created At", value="Unknown", inline=True)

        if updated_at:
            embed.add_field(
                name="🕒 Updated At",
                value=f"<t:{iso_unix_timestamp(updated_at)}:R>",
                inline=True,
            )
        else:
            embed.add_field(name="🕒 Updated At", value="Unknown", inline=True)

        topics = data.get("topics", [])
        if topics:
            embed.add_field(name="🔗 Topics", value=", ".join(topics), inline=False)
        else:
            embed.add_field(
                name="🔗 Topics", value="No topics available.", inline=False
            )

        await ctx.followup.send(embed=embed)

    @info.command(
        name="shouldhavedone", description="Get Information About ShouldHaveDone ?"
    )
    async def yars(self, ctx):
        await ctx.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/repos/SpreadSheets600/ShouldHaveDoneIt-BOT"
            ) as response:
                if response.status != 200:
                    await ctx.followup.send(
                        f"Error fetching repository data: {response.status}"
                    )
                    return

                data = await response.json()

        embed = discord.Embed(
            title="YARS Repository Information",
            description=f"{data.get("description", "No description available.")}\n### Language : {data['language']}\n",
            color=discord.Color.blue(),
            url=data.get("html_url", ""),
        )

        embed.set_author(
            name=f"Created By : {data.get("owner", {}).get("login", "Unknown")}",
            icon_url=data.get("owner", {}).get("avatar_url", ""),
        )

        embed.add_field(name="🍴 Forks", value=data.get("forks_count", 0), inline=True)
        embed.add_field(
            name="⭐ Stars", value=data.get("stargazers_count", 0), inline=True
        )
        embed.add_field(
            name="👀 Watchers", value=data.get("watchers_count", 0), inline=True
        )
        embed.add_field(
            name="📝 Open Issues", value=data.get("open_issues_count", 0), inline=True
        )

        created_at = data.get("created_at", None)
        updated_at = data.get("updated_at", None)

        if created_at:
            embed.add_field(
                name="🕒 Created At",
                value=f"<t:{iso_unix_timestamp(created_at)}:R>",
                inline=True,
            )
        else:
            embed.add_field(name="🕒 Created At", value="Unknown", inline=True)

        if updated_at:
            embed.add_field(
                name="🕒 Updated At",
                value=f"<t:{iso_unix_timestamp(updated_at)}:R>",
                inline=True,
            )
        else:
            embed.add_field(name="🕒 Updated At", value="Unknown", inline=True)

        topics = data.get("topics", [])
        if topics:
            embed.add_field(name="🔗 Topics", value=", ".join(topics), inline=False)
        else:
            embed.add_field(
                name="🔗 Topics", value="No topics available.", inline=False
            )

        await ctx.followup.send(embed=embed)


class ProfileLinks(discord.ui.View):
    def __init__(self, twitter=None, blog=None):
        super().__init__()
        self.twitter = twitter
        self.blog = blog

        if self.twitter != None:
            self.add_item(discord.ui.Button(label="Twitter ( x )", url=self.twitter))
        if self.blog != None:
            self.add_item(discord.ui.Button(label="Blog", url=self.blog))


def setup(bot: commands.Bot):
    bot.add_cog(GitHub(bot))
