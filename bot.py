import discord
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
from colorama import init, Fore, Style

#Initialize colorama
init()

game_active = False
R = None
score = 0
prefix = "n!"

def factorial(n):
    return math.factorial(n)

def log(base, x):
    return math.log(x, base)

custom_namespace = {"factorial": factorial, "log": log, "sqrt": math.sqrt}

class Response():
    text = ""
    text_og = ""
    def __init__(self, text):
        self.text = text
        self.text_og = text
        self.calculate()
    def __str__(self):
        return str(self.text)
    def calculate(self):
        self.text = custom_eval(self.text)
        self.text = eval(self.text, custom_namespace)
    def __eq__(self, other):
        return float(self.text) == float(other)
    def validity(self, rules_must, rules_cant):
        for char in rules_must:
            if char not in self.text_og:
                return False
        for char in rules_cant:
            if char in self.text_og:
                return False
        #Check for non-numerical values around operators of *, +, /, -
        for i in range(len(list(str(self.text_og)))):
            if str(self.text_og)[i] in ["*", "+", "/", "-"]:
                if i == len(list(str(self.text_og)))-1:
                    return False
                if (not str(self.text_og)[i-1].isdigit() and not str(self.text_og)[i-1]==" ") or (not str(self.text_og)[i+1].isdigit() and not str(self.text_og)[i+1]==" "):
                    return False
        return True
            

class Request():
    value = 0
    request_text = ""
    args = []
    args_must = []
    args_cant = []
    difficulty = ""
    def __init__(self, args, args_must, args_cant):
        self.value = args[0]
        self.args = args
        self.produce(args)
        if "log" in args_must and ("+" in args_cant or "-" in args_cant):
            self.difficulty = "Hard"
        elif "sqrt" in args_must and ("+" in args_cant or "-" in args_cant):
            self.difficulty = "Medium"
        elif "!" in args_must:
            self.difficulty = "Medium"
        else:
            self.difficulty = "Easy"
    def produce(self, args):
        #Produce request text
        self.request_text = produce_r_text(args)
    def __str__(self):
        return str(self.request_text)
    def __eq__(self, other):
        return self.value == other
    def get_args_must(self):
        return self.args_must
    def get_args_cant(self):
        return self.args_cant


def new_request(args):
    return Request(args[0], args[1], args[2])

def produce_r_text(args):
    value = args[0]
    text = []
    text.append("You must produce the value: **" + str(value) + "** with the following operators:" + "\n")
    for i in range(1, len(args)):
        if args[i] == "1":
            text.append("You must use:")
        elif args[i] == "0":
            text.append("\n")
            text.append("You can't use:")
        elif args[i] == "-":
            text.append("subtraction")
        elif args[i] == "+":
            text.append("addition")
        elif args[i] == "*":
            text.append("multiplication")
        elif args[i] == "/":
                text.append("division")
        elif args[i] == "^":
            text.append("exponentiation")
        elif args[i] == "sqrt":
            text.append("square root")
        elif args[i] == "log":
            text.append("logarithm")
        elif args[i] == "!":
            text.append("factorial")
        else:
            text.append("unknown operator")
    text = " ".join(text)
    return text
        
def new_args():
    all_operators = ["-", "+", "*", "/", "^", "sqrt", "log", "!"]
    args = []
    args.append(random.randint(1, 500))
    args.append("1")
    current_time = datetime.datetime.now().time()
    seed_1 = math.floor(0.1 * current_time.hour + 0.1 * current_time.minute + 0.7 * current_time.second + 0.1 * current_time.microsecond) % len(all_operators)
    args_must = []
    current_time = datetime.datetime.now().time()
    seed_2 = math.floor(0.1 * current_time.hour + 0.1 * current_time.minute + 0.1 * current_time.second + 0.7 * current_time.microsecond) % len(all_operators)
    if seed_1 == seed_2:
        seed_2 = (seed_2 + 1) % len(all_operators)
    args_cant = []
    args.append(all_operators[seed_1])
    args.append("0")
    args.append(all_operators[seed_2])
    args_must.append(all_operators[seed_1])
    args_cant.append(all_operators[seed_2])
    return args, args_must, args_cant

def main():
    """#Load config
    with open("config.json") as f:
        try:
            config = json.load(f)
        except:
            print("Error loading config.json")
            config = {}
    
    #Load prefix
    with open("prefix.txt") as f:
        try:
            prefix = f.read()
        except:
            prefix = ""
            print("Error loading prefix.txt")
    """
    #Load token
    with open("token.txt") as f:
        try:
            token = f.read()
        except:
            print("Error loading token.txt")
            token = ""
    #Load bot
    intents = discord.Intents.default()
    intents.messages = True
    bot = commands.Bot(command_prefix="n!", intents=discord.Intents.all())
    #Load cogs
    bot.load_extension("cogs.ping")
    bot.load_extension("cogs.help")
    bot.load_extension("cogs.info")
    bot.load_extension("cogs.math")
    bot.load_extension("cogs.misc")
    #Load commands
    bot.load_extension("cogs.commands")
    #Load events
    bot.load_extension("cogs.events")
    #Load responses
    bot.load_extension("cogs.responses")
    #Load requests
    bot.load_extension("cogs.requests")
    #Load other
    bot.load_extension("cogs.other")
    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')
        guild = bot.guilds[0]
        all_channels = guild.channels

    bot.remove_command('help')
    @bot.command()
    async def help(ctx):
        global game_active, R, score, prefix
        await ctx.send("Use n!start to start a new game and n!stop to end the game")

    bot.remove_command('start')
    @bot.command()
    async def start(ctx):
        global game_active, R, score, prefix
        if game_active == False:
            await ctx.send("Started a new game!")
            game_active = True
            R = new_request(new_args())
            await ctx.send(remove_fore(str(R)))
        else:
            await ctx.send("Game is already active!")

    bot.remove_command('stop')
    @bot.command()
    async def stop(ctx):
        global game_active, R, score, prefix 
        if game_active == True:
            await ctx.send("Stopped the game!")
            game_active = False
        else:
            await ctx.send("There is no active game!")

    bot.remove_command('score')
    @bot.command()
    async def score(ctx):
        global game_active, R, score, prefix
        await ctx.send("Current Score : " + str(score))
    
    @bot.event
    async def on_message(message):    
        global game_active, R, score, prefix
        print(message.content)
        if message.content.startswith("n!score"):
            await bot.process_commands(message)
            return
        if game_active:
            #Check if message is a response
            ch = message.channel
            RES = Response(reduce_space(message.content))
            if RES.validity(R.get_args_must(), R.get_args_cant()) and math.ceil(float(str(RES))) == math.ceil(float(str(R.value))):
                await ch.send("Correct!")
                score += 1
                message.add_reaction(bot.get_emoji("white_check_mark"))
            elif RES.validity(R.get_args_must(), R.get_args_cant()):
                await ch.send("Incorrect!")
                score -= 1
                message.add_reaction(bot.get_emoji("fockos"))
            else:
                await ch.send("Invalid!")
                score -= 1
                message.add_reaction(bot.get_emoji("fockos"))
            R = new_request(new_args())
            await ch.send(remove_fore(str(R)))
        await bot.process_commands(message)

    

    #Run bot
    bot.run(token)

def test():
    for i in range(100):
        print(Fore.LIGHTYELLOW_EX + "=================================================")
        R = new_request(new_args())
        print(Fore.WHITE + str(R) + "\n")
        print(Fore.WHITE + "Difficulty: " + Fore.YELLOW + R.difficulty + "\n")
        RES = Response(reduce_space(input(Fore.WHITE + "Your response: ")))
        print("Equals to " + Fore.YELLOW + str(RES) + "\n")
        print(Fore.WHITE + "Expected: " + Fore.YELLOW + str(R.value) + "\n")
        if RES.validity(R.get_args_must(), R.get_args_cant()) and math.ceil(float(str(RES))) == math.ceil(float(str(R.value))):
            print(Fore.GREEN + "Correct!" + "\n")
        elif not RES.validity(R.get_args_must(), R.get_args_cant()):
            print(Fore.RED + "Invalid! The rules are violated." + "\n")
        else:
            print(Fore.RED + "Incorrect!" + "\n")

def custom_eval(expression):
    # Split the expression by spaces
    parts = expression.split()
    
    # Iterate through parts and replace factorial expressions
    for i in range(len(parts)):
        if "!" in parts[i]:
            # Extract the number before the factorial symbol
            num = parts[i].split("!")[0]
            
            # Replace the factorial expression with a function call
            parts[i] = parts[i].replace(num + "!", "factorial(" + num + ")")
    
    # Join the modified parts back into a single expression string
    modified_expression = " ".join(parts)
    return modified_expression

def reduce_space(expression):
    exp = list(expression)
    for i in range(len(expression)-1):
        if exp[i] == " " and exp[i+1] == " ":
            exp[i+1] = ""
    return "".join(exp)

def remove_fore(expression):
    pattern = r'Fore\.[^\s]+'

    # Use re.sub() to replace all occurrences of "Fore...." with an empty string
    result = re.sub(pattern, '', expression)

    return result

main()
