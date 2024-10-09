import discord
from meta_ai_api import MetaAI
from discord.ext import commands
from discord import SlashCommandGroup

ai = MetaAI()


class AI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.conversations = {}

    def get_conversation_context(self, user_id):

        history = self.conversations.get(user_id, [])
        return "\n\n".join(
            [f"User: {item['query']}\nMetu: {item['response']}" for item in history]
        )

    @commands.slash_command(name="ask", description="Ask Metu Anything")
    async def ask(self, ctx, query: str):
        await ctx.defer()
        user_id = str(ctx.author.id)

        if user_id not in self.conversations:
            self.conversations[user_id] = []

        try:

            pre_instruction = "You are Metu, a friendly, knowledgeable assistant trained by SOHAM. You always provide clear and detailed answers in a polite and helpful tone."

            conversation_context = self.get_conversation_context(user_id)

            full_query = f"{pre_instruction}\n\n{conversation_context}\n\nUser: {query}"

            response = ai.prompt(message=full_query)
            message = response.get("message", "I'm Sorry, Metu Might Be Dead ?!")
            media = response.get("media", [])

            self.conversations[user_id].append({"query": query, "response": message})
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

    history = SlashCommandGroup(name="history", description="Conversation History")

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
            description="Your Conversation History Have Been Cleared",
        )
        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        user_id = str(message.author.id)

        if user_id not in self.conversations:
            self.conversations[user_id] = []

        channel = message.channel

        try:
            query = message.content
            pre_instruction = "You are Metu, a friendly, knowledgeable assistant trained by SOHAM. You always provide clear and detailed answers in a polite and helpful tone."

            conversation_context = self.get_conversation_context(user_id)

            full_query = f"{pre_instruction}\n\n{conversation_context}\n\nUser: {query}"

            response = ai.prompt(message=full_query)
            message = response.get("message", "I'm Sorry, Metu Might Be Dead ?!")
            media = response.get("media", [])

            self.conversations[user_id].append({"query": query, "response": message})
            channel = message.channel
            await channel.send(message)

        except Exception as e:
            channel = message.channel
            await channel.send(message)


def setup(bot: commands.Bot):
    bot.add_cog(AI(bot))
