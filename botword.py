import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import os
import time
import datetime
import json
import requests
import pytz
import psutil
import math
import re
import string
import warnings
from colorama import init, Fore, Style

all_words = []
#Load words
with open("words.txt") as f:
    try:
        all_words = f.read().splitlines()
    except:
        print("Error loading words.txt")
for i in range(5):
    print(all_words[i])

game_active = False
combo = 0
channel_id = 0
MyRequest = None
s1 = ""

def pick_letter_start():
    return random.choice(string.ascii_letters).lower()

def pick_letter_end():
    letter = random.choice(string.ascii_letters).lower()
    while letter in ['z', 'x', 'c', 'v', 'b', 'n', 'o', 'i', 'u', 'a', 'g', 'j', 'q']:
        letter = random.choice(string.ascii_letters).lower()
    return letter

class Response():
    text = ""
    def __init__(self, text):
        self.text = fix_text(text)
    def validate(self):
        for letter in self.text:
            if letter not in string.ascii_letters:
                return False
        return True
    def __str__(self):
        return str(self.text)
    def correctness(self, let_1, let_2):
        TL = list(self.text)
        if TL[0] == let_1 and TL[len(TL) - 1] == let_2 and self.text in all_words:
            return True
        else:
            return False

class Request():
    first = ''
    last = ''
    def __init__(self):
        word_exists = False
        while not word_exists:
            self.first = pick_letter_start()
            self.last = pick_letter_end()
            for word in all_words:
                if word[0] == self.first and word[len(word) - 1] == self.last:
                    if self.first == 'z' or self.first == 'x' and random.randint(0, 4) == 1:
                        continue
                    word_exists = True
    def message(self):
        return "You must produce a word that starts with **" + self.first.upper() + "** and ends with **" + self.last.upper() + "**."
    def first_letter(self):
        return self.first
    def last_letter(self):
        return self.last

def fix_text(text):
    return text.replace(" ", "").lower()

def new_request():
    return Request()

def main():
    Request = None
    
    client = discord.Client(intents=discord.Intents.all())

    token = ""
    with open("token.txt") as f:
        try:
            token = f.read()
        except:
            print("Error loading token.txt")

    tree = app_commands.CommandTree(client)

    print("------")

    @tree.command(name="hello", description="Say hello to the bot!")
    async def hello(ctx):
        await ctx.response.send_message(f"Hello, {ctx.user}!")

    @client.event
    async def on_ready():
        print("Logged in as " + client.user.name)
        print("ID: " + str(client.user.id))
        print("------")
    
    @tree.command(name="start", description="Start the game!")
    async def start(ctx):
        global game_active, channel_id, MyRequest
        channel_id = ctx.channel.id
        if game_active == False:
            game_active = True
            MyRequest = new_request()
            await ctx.response.send_message("Game started! \n" + MyRequest.message())
        else:
            await ctx.followup.send("Game already started!")

    @tree.command(name="stop", description="Stop the game!")
    async def stop(ctx):
        global game_active
        if game_active == True:
            game_active = False
            await ctx. response.send_message("Game stopped!")
        else:
            await ctx. response.send_message("No game active!")

    @tree.command(name="score", description="Get the current combo")
    async def score(ctx):
        global combo
        await ctx. response.send_message("Current combo: " + str(combo))

    @tree.command(name="clear", description="Clear the last amount of messages")
    async def clear(ctx , amount : int):
        #Delete the last amount of messages
        await ctx.channel.purge(limit=int(amount))

    @tree.command(name="help", description="Get help with the bot")
    async def help(ctx  ):
        await ctx. response.send_message("Use `/start` to start a new game and `/stop` to end the game")

    @tree.command(name="ping", description="Ping the bot")
    async def ping(ctx  ):
        await ctx. response.send_message("Pong!")

    @client.event
    async def on_message(message):
        global game_active, channel_id, MyRequest, combo, s1
        ctx = message.channel
        if message.content.startswith("/start") or message.content.startswith("/stop") or message.content.startswith("/score") or message.content.startswith("/clear") or message.content.startswith("/help") or message.content.startswith("/ping"):
        #    await client.process_commands(message)
            return
        if game_active == True and message.channel.id == channel_id and message.author.id!= client.user.id:
            R = Response(message.content.lower())
            if R.validate():
                if R.correctness(MyRequest.first_letter(), MyRequest.last_letter()):
                    combo += 1
                    s1 = ""
                    if combo % 5 == 0:
                        s1 = "You got a combo of " + str(combo) + "! Great job."
                    await ctx. send("Correct!" + "\n" + str(s1))
                else:
                    await ctx. send("Incorrect!")
                    combo = 0
            else:
                await ctx. send("Invalid response!")
                combo = 0
            MyRequest = new_request()
            await ctx. send(MyRequest.message())

    @client.event 
    async def on_connect():
        await tree.sync()
        print("Commands registered successfully.")

    @client.event
    async def on_ready():
        await client.change_presence(activity=discord.Game(name="/help"))


    client.run(token)

main()