import discord
from discord import app_commands
from discord.ext import commands
import random
import os
import requests
import math
import string

def string_to_int_convert(text):
    # Converts each text to a series of digits based on the characters of the input
    # Essientially a name to id conversion
    n = 0
    i = 1
    j = 0
    char_ = [ord(text[0])]
    start_ = 0
    end_ = 0
    for char in text:
        j += 1
        if ord(char) > char_[-1]:
            char_.append(ord(char))
            end_ = j
        else:
            char_ = [ord(char)]
            start_ = j
        n = n + (ord(char) - 96) * i
        i *= 6
        if char == 'a' or char == 'A' or char == '0' and i == 6**2:
            n = n + 1
        if char == 'b' or char == 'B' or char == 'd' or char == 'D' and i == 6**3:
            n = n + 2
    n += (sum(char_) + start_ + end_ % 60)
    #Limit n to its last 5 digits
    n = n % 10**5
    return n

all_words = []
#Load words
with open("words.txt") as f:
    try:
        all_words = f.read().splitlines()
    except:
        print("Error loading words.txt")
for i in range(5):
    print(all_words[i])

games_ = {
    # channel-server : true/false
}

combo_ = {
    # channel-server : combo
}

requests_ = {
    # channel-server : request
}

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
                    if self.first == 'z' or self.first == 'x' and random.randint(0, 13) == 1:
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
        print("id: " + str(client.user.id))
        print("------")
    
    @tree.command(name="start", description="Start the game!")
    async def start(ctx):
        global channel_id, games_, requests_
        channel_id = string_to_int_convert(ctx.channel.name)
        if games_.get(int(str(string_to_int_convert(ctx.channel.name)) + str(ctx.guild.id))) == None or games_[int(str(string_to_int_convert(ctx.channel.name)) + str(ctx.guild.id))] == False:
            games_[int(str(string_to_int_convert(ctx.channel.name)) + str(ctx.guild.id))] = True
            combo_[int(str(string_to_int_convert(ctx.channel.name)) + str(ctx.guild.id))] = 0
            print("Addition: " + str(games_))
            requests_[int(str(string_to_int_convert(ctx.channel.name)) + str(ctx.guild.id))] = new_request()
            myrequest = requests_[int(str(string_to_int_convert(ctx.channel.name)) + str(ctx.guild.id))]
            await ctx.response.send_message("Game started! \n" + myrequest.message())
        else:
            await ctx.response.send_message("Game already started!")

    @tree.command(name="stop", description="Stop the game!")
    async def stop(ctx):
        global games_
        if games_[int(str(string_to_int_convert(ctx.channel.name)) + str(ctx.guild.id))] == True:
            games_[int(str(string_to_int_convert(ctx.channel.name)) + str(ctx.guild.id))] = False
            combo_[int(str(string_to_int_convert(ctx.channel.name)) + str(ctx.guild.id))] = 0
            await ctx. response.send_message("Game stopped!")
        else:
            await ctx. response.send_message("No game active!")

    @tree.command(name="score", description="Get the current combo")
    async def score(ctx):
        global combo_
        combo = combo_[int(str(string_to_int_convert(ctx.channel.name)) + str(ctx.guild.id))]
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
        global channel_id, combo_, games_, s1, requests_
        ctx = message.channel
        myrequest = requests_[int(str(string_to_int_convert(ctx.name)) + str(ctx.guild.id))]
        if message.content.startswith("/start") or message.content.startswith("/stop") or message.content.startswith("/score") or message.content.startswith("/clear") or message.content.startswith("/help") or message.content.startswith("/ping"):
        #    await client.process_commands(message)
            return
        if games_.get(int(str(string_to_int_convert(ctx.name)) + str(ctx.guild.id))) == None:
            return
        if games_[int(str(string_to_int_convert(ctx.name)) + str(ctx.guild.id))] == True and message.author.id!= client.user.id:
            R = Response(message.content.lower())
            if R.validate():
                if R.correctness(myrequest.first_letter(), myrequest.last_letter()):
                    combo_[int(str(string_to_int_convert(ctx.name)) + str(ctx.guild.id))] += 1
                    s1 = ""
                    if combo_[int(str(string_to_int_convert(ctx.name)) + str(ctx.guild.id))] % 5 == 0:
                        s1 = "You got a combo of " + str(combo_[int(str(string_to_int_convert(ctx.name)) + str(ctx.guild.id))]) + "! Great job."
                    await ctx. send("Correct!" + "\n" + str(s1))
                else:
                    await ctx. send("Incorrect!")
                    combo_[int(str(string_to_int_convert(ctx.name)) + str(ctx.guild.id))] = 0
            else:
                await ctx. send("Invalid response!")
                combo_[int(str(string_to_int_convert(ctx.name)) + str(ctx.guild.id))] = 0
            requests_[int(str(string_to_int_convert(ctx.name)) + str(ctx.guild.id))] = new_request()
            myrequest = requests_[int(str(string_to_int_convert(ctx.name)) + str(ctx.guild.id))]
            await ctx. send(myrequest.message())

    @client.event 
    async def on_connect():
        await tree.sync()
        print("Commands registered successfully.")

    @client.event
    async def on_ready():
        await client.change_presence(activity=discord.Game(name="/help"))


    client.run(token)

main()