import discord
from meta_ai_api import MetaAI
from discord.ext import commands
from discord import SlashCommandGroup

ai = MetaAI()

analysis_template = """
You are an AI assistant specialized in analyzing conversation with users. Your task is to analyze the given user's conversations with you and provide insights into their personality, interests, and behavior.

Given the user's conversation history, please provide an analysis focusing on the following aspects:

1. Personality Traits: Identify key personality traits based on the user's comments.
2. Interests & Passions: Determine the user's main interests and passions from their subreddit choices and comment content.
3. Communication Style: Describe how the user typically engages with others on Reddit.
4. Social Behavior: Infer the user's social interaction tendencies on the platform.
5. Recurring Themes: Identify any patterns or repeated themes in the user's comments.
"""


class AI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.conversations = {}
        self.user_profiles = {}

    def get_conversation_context(self, user_id):
        history = self.conversations.get(user_id, [])
        return "\n\n".join(
            [f"User: {item['query']}\nMetu: {item['response']}" for item in history]
        )

    def get_user_profile(self, user_id):
        return self.user_profiles.get(
            user_id, {"tone": "neutral", "formality": "medium"}
        )

    @commands.slash_command(name="ask", description="Ask Metu Anything")
    async def ask(self, ctx, query: str):
        await ctx.defer()
        user_id = str(ctx.author.id)

        if user_id not in self.conversations:
            self.conversations[user_id] = []

        try:
            profile = self.get_user_profile(user_id)
            pre_instruction = f"You are Metu, a friendly, knowledgeable assistant trained by SOHAM. Please respond in a {profile['tone']} tone and with {profile['formality']} formality."

            conversation_context = self.get_conversation_context(user_id)
            full_query = f"{pre_instruction}\n\n{conversation_context}\n\nUser: {query}"

            async with ctx.typing():
                response = ai.prompt(message=full_query)
            message = response.get("message", "I'm Sorry, Metu Might Be Dead ?!")
            media = response.get("media", [])

            self.conversations[user_id].append({"query": query, "response": message})

            if len(self.conversations[user_id]) > 10:
                thread = await ctx.channel.create_thread(
                    name=f"Conversation with {ctx.author.name}", message=ctx.message
                )
                await thread.send(message)
            else:
                await ctx.followup.send(message)

            if media:
                for item in media:
                    image_url = item.get("url")
                    if image_url:
                        embed = discord.Embed(
                            title="Generated Image",
                            description=f"Prompt: {item.get('prompt', 'N/A')}",
                        )
                        embed.set_image(url=image_url)
                        await ctx.followup.send(embed=embed)

        except Exception as e:
            await ctx.followup.send(f"An Error Occurred: {e}")

    ai = SlashCommandGroup(name="ai", description="AI Commands")
    history = ai.create_subgroup(name="history", description="Conversation History")

    @history.command(
        name="recall", description="Recall Your Conversation History With Metu"
    )
    async def recall(self, ctx):
        user_id = str(ctx.author.id)
        if user_id in self.conversations and self.conversations[user_id]:
            history = "\n\n".join(
                [
                    f"**You:** {conv['query']}\n**Metu:** {conv['response']}"
                    for conv in self.conversations[user_id]
                ]
            )
            await ctx.respond(f"**Your Conversation History:**\n\n{history}")
        else:
            await ctx.respond("You Have No Conversation History With Metu")

    @history.command(name="clear", description="Start A New Conversation With Metu AI")
    async def clear(self, ctx):
        user_id = str(ctx.author.id)
        self.conversations[user_id] = []

        embed = discord.Embed(
            title="New Conversation Started",
            description="Your Conversation History Has Been Cleared",
        )
        await ctx.respond(embed=embed)

    @ai.command(name="stats", description="Get Your Interaction Stats With Metu")
    async def stats(self, ctx):
        user_id = str(ctx.author.id)
        total_questions = (
            len(self.conversations[user_id]) if user_id in self.conversations else 0
        )

        user_data = (
            f"{analysis_template}\n\nUser: {self.get_conversation_context(user_id)}"
        )
        charcter_analysis = ai.prompt(message=user_data).get("message", "N/A")

        await ctx.respond(
            f"**Total Questions Asked:** {total_questions}\n\n**Character Analysis:**\n{charcter_analysis}"
        )

    @ai.command(name="summarize", description="Summarize The Last 50 Messages Metu")
    async def summarize(self, ctx):
        user_id = str(ctx.author.id)
        if user_id in self.conversations and self.conversations[user_id]:
            conversation_context = self.get_conversation_context(user_id)
            last_50 = "\n\n".join(conversation_context.split("\n\n")[-50:])
            summary = ai.summarize(last_50)
            await ctx.respond(f"Here Is The Summary Of Our Conversation:\n\n{summary}")
        else:
            await ctx.respond("No Conversation History Found")

    @ai.command(name="preference", description="Set your preferences for Metu")
    async def set_preferences(self, ctx, tone: str, formality: str):
        user_id = str(ctx.author.id)
        self.user_profiles[user_id] = {"tone": tone, "formality": formality}
        await ctx.respond("Your Preferences Have Been Updated")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        user_id = str(message.author.id)

        if self.bot.user in message.mentions:
            if user_id not in self.conversations:
                self.conversations[user_id] = []

            try:
                query = message.content
                profile = self.get_user_profile(user_id)
                pre_instruction = f"You are Metu, a friendly, knowledgeable assistant trained by SOHAM. Please respond in a {profile['tone']} tone and with {profile['formality']} formality."

                conversation_context = self.get_conversation_context(user_id)
                full_query = (
                    f"{pre_instruction}\n\n{conversation_context}\n\nUser: {query}"
                )

                async with message.channel.typing():
                    response = ai.prompt(message=full_query)
                reply_message = response.get(
                    "message", "I'm Sorry, Metu Might Be Dead ?!"
                )
                media = response.get("media", [])

                self.conversations[user_id].append(
                    {"query": query, "response": reply_message}
                )

                # Responding in thread if needed
                if len(self.conversations[user_id]) > 10:
                    thread = await message.channel.create_thread(
                        name=f"Conversation With {message.author.name}", message=message
                    )
                    await thread.send(reply_message)
                else:
                    await message.channel.send(reply_message)

                if media:
                    for item in media:
                        image_url = item.get("url")
                        if image_url:
                            embed = discord.Embed(
                                title="Generated Image",
                                description=f"Prompt: {item.get('prompt', 'N/A')}",
                            )
                            embed.set_image(url=image_url)
                            await message.channel.send(embed=embed)

            except Exception as e:
                await message.channel.send(f"An error occurred: {e}")


def setup(bot: commands.Bot):
    bot.add_cog(AI(bot))
