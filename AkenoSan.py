from discord.ext import commands
import asyncio
import os
import json
from datetime import datetime
import subprocess
import time
from io import StringIO
from contextlib import redirect_stdout

TOKEN = os.getenv('AKENOSAN_TOKEN')
CCDIR = "custom_commands"
CC = {} # List that holds all commands in memory

OWNER_IDS = [
    "205166483284819969",   # Knifesurge#1723
    "318644989556949003"    # Carlos94563#0697
]

bot = commands.Bot(command_prefix='!', description="""
AkenoSan is a Discord Bot written in Discord.py by Knifesurge#1723. Please contact me
if you have any problems with the bot. Have a great day!
""")

# REMINDER: You can't use on_message and the command() decorators at the same time,
# only the on_message event will fire and not the commands

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    if not os.path.exists(CCDIR):
        os.mkdir(CCDIR)
        print('Custom Command Directory Created!')
    else:
        print('Custom Command Directory exists...')

@bot.command(name="sd", hidden=True)
async def shutdown(ctx):
    if str(ctx.author.id) in OWNER_IDS:
        print("\n\n\n{}\n\t\tSHUTTING DOWN THE BOT!!!!!\n{}\n\n\n".format("="*70,"="*70))
        await bot.logout()
        exit()

@bot.command(name="rt", hidden=True)
async def restart(ctx):
    print(f'{ctx.author.name} ({ctx.author.id})')
    if str(ctx.author.id) in OWNER_IDS:
        cmd = 'py AkenoSan.py'
        print("\n\n\n{}\n\t\tRESTARTING THE BOT!!!!!\n{}\n\n\n".format("="*60,"="*60))
        subprocess.run(cmd, shell=True)
        time.sleep(0.2)
        quit()

@bot.command()
async def test(ctx):
    counter = 0
    tmp = await ctx.channel.send('Calculating messages...')
    async for log in ctx.channel.history().filter(lambda m: m.author == ctx.author):
        counter += 1
    await tmp.edit(content='You have {} messages!'.format(counter))

@bot.command()
async def sleep(ctx):
    await asyncio.sleep(5)
    await ctx.channel.send('Done sleeping')

@bot.command(name="rc", hidden=True)
async def run_command(ctx, name : str):
    cmd = None
    found = False
    count = 0
    while not found and count < len(CC["commands"]):
        command = CC["commands"][count]
        if command['name'] == name:
            cmd = command
            found = True
        count += 1

    if not found:
        # Couldn't find the command, so don't try to run it
        await ctx.send(f'Sorry! I cannot find the command {name}!')
        return
    last_run = cmd['last_ran']
    try:
        # Command found, so run and send message of result
        f = StringIO()
        with redirect_stdout(f):
            exec(cmd['body'])   # Try and run the command
        result = f.getvalue()
        cmd['last_run'] = datetime.now().strftime('%c') # Update the last time the cmd was run
        await ctx.send(result)
    except:
        await ctx.send(f'There was an error running the command {name}')
        cmd['last_run'] = last_run

@bot.command(name="ccc", hidden=True)
async def clear_custom_commands(ctx):
    global CC
    CC = {"commands": []}
    os.remove('custom_commands\\cc.json')
    with open('custom_commands\\cc.json', 'w') as f:
        json.dump(CC, f, indent=4)
    await ctx.send("Custom commands cleared! Please reload.")

@bot.command(name="cc", hidden=True)
async def create_command(ctx, name : str, body : str):
    global CC

    if CC is {}:
        CC = {"commands": []}

    data = CC

    found = False
    count = 0
    while not found and count < len(CC["commands"]):
        command = CC["commands"][count]
        if command['name'] == name:
            found = True
        count += 1

    if found:
        # Command already exists, expecting an update
        cmd = data["commands"][count-1]
    else:
        data["commands"].append({}) # Create a new dict for the new command
        cmd = data["commands"][-1] # Point the cmd to the empty dict
        cmd['name'] = name

    print(f'Whole message: {ctx.message.content}')

    if body == "```":
        # Using a block, process accordingly
        message = ctx.message.content[len('!cc')+1+len(name)+1+3:-3] # Strip command, name, the three ticks, and the 2 spaces in between, then the last 3 ticks
        print(f'Message to process: {message}')
        cmd['body'] = message
    else:
        # No spaces
        cmd['body'] = body

    cmd['created'] = datetime.now().strftime('%c')
    cmd['last_ran'] = ''
    
    print(data)
    with open('custom_commands\\cc.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)
    print(f'Dumped custom command {name} to custom command file! Please reload the commands!')
    await ctx.send('Custom command created!')

@bot.command(name="lc", hidden=True)
async def load_commands(ctx):
    global CC
    with open('custom_commands\\cc.json') as f:
        CC = json.load(f)
        for cmd in CC['commands']:
            print("="*30)
            for key in cmd.keys():
                print(f'{key.upper()}: {cmd[key]}')
            print("="*30)

@bot.command(name='lcc', hidden=True)
async def list_custom_commands(ctx):
    global CC
    message = []
    message.append("Custom Commands\n{}\n".format("="*30))
    for cmd in CC['commands']:
        message.append(cmd['name']+'\n')
        message.append('-'*30+'\n')
    await ctx.send("".join(message))

@bot.command(name='lcmds', hidden=True)
async def list_commands(ctx):
    print("{}\n{}\n{}".format("="*12,"Commands ("+str(len(bot.all_commands))+")","="*12))
    for cmd in bot.all_commands:
        print(cmd)

@bot.command(name='hw', help='Says "Hello, World!"')
async def helloworld(ctx):
    print('>> Command: helloworld')
    await ctx.send('Hello, World!')

bot.run(TOKEN)
