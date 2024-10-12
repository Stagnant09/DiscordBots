# @Stagnant09 2024
# Discord Bot

import discord
from discord import app_commands
from discord.ext import commands
import asyncio

emojis_ = {
    "👍": 1,
    "👎": -1,
}

# Read env.env and get token
with open('env.env', 'r') as file:
    TOKEN = file.read().strip()

intents = discord.Intents.all()
intents.members = True

# Use slash commands
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@tree.command(name="hey", description="Say hello to the bot")
async def hey(ctx):
    await ctx.response.send_message(f"Hello, {ctx.user}!")


@bot.event
async def on_connect():
    await tree.sync(guild=discord.Object(id=1068860796840448010))
    print("Commands registered successfully.")

@tree.command(name="user", description="Calculates the score of a user based on the reactions he/she has received.", guild=discord.Object(id=1068860796840448010))
async def user(interaction: discord.Interaction, arg: str):
    await interaction.response.send_message(f"**Calculating {arg}'s score...**", ephemeral=True)
    bot.loop.create_task(calculateScore(interaction, arg))

async def calculateScore(interaction: discord.Interaction, user: str):
    idd = 0
    score = 0
    for channel in bot.get_all_channels():
        if channel.type == discord.ChannelType.text:
            # Make an iterable object from channel.history(limit=100)
            async for message in channel.history(limit=2000):
                if message.author.name == user:
                    idd += 1
                    print(user + "\'" + " message " + str(idd))
                    for reaction in message.reactions:
                        if isinstance(reaction.emoji, str):
                            emoji_name = reaction.emoji
                        else:
                            emoji_name = reaction.emoji.name
                        if emoji_name in emojis_:
                            score += emojis_[emoji_name]

    await interaction.followup.send(f"**{user}'s score is {score}**.\n" + "R/M ratio = " + str(score / idd))

bot.run(TOKEN)
