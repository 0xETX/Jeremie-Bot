#===NOTE===
#Wand may require either of the packages below to be installed
#Windows: https://imagemagick.org/script/download.php#windows, https://docs.wand-py.org/en/0.6.2/guide/install.html
#Linux (Debian): apt-get install libmagickwand-dev
import os
import discord
from utils import *
import re
import asyncio
import random
import subprocess
import urllib.request
import Augmentor
import sqlite3
import requests
from shutil import rmtree
from time import sleep
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.commands import Option
from threading import Thread
from glob import glob
from wand.image import Image
from wand.display import display

# Deletes created temp files. 1 = Delete output, 0 = Keep output.
deleteOutput = 1

# Env token loading
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot Strings
prefix = "jr!"
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix = prefix, intents=intents)

# Custom command groups
custom = client.create_group("custom", "Custom command creation.")

# Others
validUrl = r"[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([\-a-zA-Z0-9@:%_\+\.~#?&\/=]*\.(jpg|jpeg|png))"

# Prints if bot successfully runs
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

"""
#Daily Tasks
@tasks.loop(hours=24.0)
async def daily_tasks():
    animals_list = ["dog", "cat"]
    select_animal = random.choice(animals_list)
    
    if select_animal == "dog":
        dog_data = requests.get(r"https://dog.ceo/api/breeds/image/random").content
        animal_picture = requests.get(str(dog_data).split('"')[3].replace("\\", "")).content
        
    elif select_animal == "cat":
        animal_picture = requests.get(r"https://cataas.com/cat/says/%20").content
        
    else:
        print("ERROR 50: Unexpected animal result!")
        animal_picture = requests.get(r"https://cataas.com/cat/says/%20").content
        
    with open("attachments/random_animal_image.jpg", "wb") as handler:
        handler.write(animal_picture)
"""

"""
#Set Daily Animal Picture Location
@client.slash_command(name="dailyanimal", description="Set location of daily animal pictures. Administrators only. Set to 0 to disable.")
async def dailyanimal(ctx,
    channel: Option(str, "Choose the channel to post the images in.", required=True)):
    
    if ctx.message.author.mention == discord.Permissions.administrator:
        print("Admin!")
    else:
        print("Not admin!")
"""

#Random Cat Command
@client.slash_command(name="cats", description="Generates a random picture of a cat.")
async def cats(ctx):
    cat = requests.get(r"https://cataas.com/cat/says/%20").content
    filename = gen_alpha(32) + ".jpg"
    with open(f"attachments/{filename}", "wb") as handler:
        handler.write(cat)
    await ctx.respond(file=discord.File(f"attachments/{filename}"))
    os.remove("attachments/"+filename)
    
#Random Dog Command
@client.slash_command(name="dogs", description="Generates a random picture of a dog.")
async def dogs(ctx):
    dog_data = requests.get(r"https://dog.ceo/api/breeds/image/random").content
    dog = requests.get(str(dog_data).split('"')[3].replace("\\", "")).content
    filename = gen_alpha(32) + ".jpg"
    with open(f"attachments/{filename}", "wb") as handler:
        handler.write(dog)
    await ctx.respond(file=discord.File(f"attachments/{filename}"))
    os.remove("attachments/"+filename)

# Ping Command
@client.slash_command(name="ping", description="The bot pings the server to check response time. The lower, the faster the response.")
async def ping(ctx):
    await ctx.respond(f"{ctx.author.mention}, Jeremie has arrived. `({round(client.latency*1000)}ms)`")

# Test Command
@client.slash_command(name="test", description="For testing purposes.")
async def test(ctx):
    messages = await ctx.channel.history(limit=5).flatten()
    for message in messages:
        print(message.content, sep="\n")
        await ctx.respond(f"**ECHO:** {message.content}")

# Dice Roll Command
@client.slash_command(name="diceroll", description="Roll a custom dice!")
async def diceroll(ctx,
                   diceset: Option(str, "Choose the dice you wish to use. Format: <count>d<dice_value>. Count: 1-15. Dice_Value: 2-10000.", required=True),
                   modifier: Option(int, "Add or subtract a specific value from the final result. Example: 5, +5, -5.", required=False)):
    
    # Set important variables. rollcount = data, diceemoji = emojis used.
    rollcount = diceset.split("d")
    diceemoji = ["<:greatroll:1125593848475824199>", "<:averageroll:1125594666604183592>", "<:badroll:1125593850484887562>"]
    
    # Make sure the data provided is valid
    try:
        rollcount[0] = int(rollcount[0])
        rollcount[1] = int(rollcount[1])
        if not (1 <= rollcount[0] <= 15):
            await ctx.respond("Not a valid count size! Count must at least 1, at most 15.")
            return
        if not (2 <= rollcount[1] <= 10000):
            await ctx.respond("Invalid dice value! Must be minimum 2, maximum 10000.")
            return
    except:
        await ctx.respond("Invalid format! Proper format examples: 1d20, 3d6, 2d4.")
        return
    
    # Check if modifier exists and is valid
    if modifier != None:
        try:
            rollmodifier = int(modifier)
        except:
            await ctx.respond("Invalid format! Proper format examples: 7, +3, -4.")
            return
    else:
        rollmodifier = 0

    # Begin sequence
    if rollmodifier == 0:
        await ctx.respond(f"**Rolling {rollcount[0]}d{rollcount[1]}...**")
    else:
        await ctx.respond(f"**Rolling {rollcount[0]}d{rollcount[1]} with modifier {rollmodifier}...**")
    await asyncio.sleep(1.5)
    
    # Counter
    totalroll = 0
    
    # Iterate through rolls
    for rolls in range(rollcount[0]):
        rolled = random.randint(1, rollcount[1])
        totalroll += rolled
        
        if rolled == rollcount[1]:
            await ctx.send(f"{diceemoji[0]} **CRITICAL SUCCESS!** You rolled {rolled}.")
        elif (rolled / rollcount[1]) >= 0.67:
            await ctx.send(f"{diceemoji[0]} You rolled {rolled}.")
        elif rolled == 1:
            await ctx.send(f"{diceemoji[2]} **CRITICAL FAILURE!** You rolled {rolled}.")
        elif (rolled / rollcount[1]) <= 0.34:
            await ctx.send(f"{diceemoji[2]} You rolled {rolled}.")
        else:
            await ctx.send(f"{diceemoji[1]} You rolled {rolled}.")
        
        await asyncio.sleep(2.5)
    
    # Results
    if modifier == 0:
        await ctx.respond(f"**Finished rolling {rollcount[0]}d{rollcount[1]}!** (Total: {(totalroll + rollmodifier)}, Average Roll: {round(totalroll/rollcount[0], 3)}")
    else:
        await ctx.respond(f"**Finished rolling {rollcount[0]}d{rollcount[1]}!** (Total: {(totalroll + rollmodifier)}, Average Roll: {round(totalroll/rollcount[0], 3)}, Modifier: {rollmodifier})")

# Distort Command
@client.slash_command(name="distort", description="Distorts linked images into random directions. Currently supports: png, jpg, jpeg.")
async def distort(ctx,
                imagelink: Option(str, "Insert a link of the photo you wish to distort.", required=False, default=None),
                magnitude: Option(int, "Intensity of distortion. Recommended settings are -50 to 50.", required=False)):

    # Create temp folder name
    safeFolder = f"{(gen_alpha(32))}"

    # Sees if magnitude is valid
    try:
        mag = int(magnitude)
    except:
        mag = random.randint(25, 30)

    # If no link is provided, search last five messages
    if imagelink == None:
        messages = await ctx.channel.history(limit=5).flatten()
        messages.reverse()
        for msg in messages:
            # Checks to see if there are any images as attachments
            if (msg.attachments):
                for attachmentNumber in range(len(msg.attachments)):
                    if re.search(validUrl, str(msg.attachments[attachmentNumber])):
                        imagelink = (re.search(validUrl, str(msg.attachments[attachmentNumber]))).group(0)
                        break
                        
            #Checks to see if there are image links in text    
            if re.search(validUrl, msg.content):
                imagelink = (re.search(validUrl, msg.content)).group(0)
                break
                
        if imagelink == None:
            await ctx.respond("Could not locate a valid format in the past 5 messages.")
            return
         
    # Checks if extension is valid
    if imagelink[-3:] in ["png", "jpg"]:
        fileName = f"attachments/{safeFolder}/{gen_alpha(32) + imagelink[-4:]}"
    elif imagelink[-4:] in ["jpeg"]:
        fileName = f"attachments/{safeFolder}/{gen_alpha(32) + imagelink[-5:]}"
    else:
        await ctx.respond("Not a valid file or URL.")
        return

    # Creates a new folder and downloads image
    os.mkdir(f"attachments/{safeFolder}")
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1")]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(imagelink, fileName)

    # Attempts to distort and send the image
    try:
        await ctx.respond("Distorting your image. One moment...")
        picture = Augmentor.Pipeline(r"attachments/"+safeFolder)
        picture.crop_random(probability=1, percentage_area=0.9)
        picture.random_distortion(probability=1, grid_width=random.randint(4, 7), grid_height=random.randint(8,12), magnitude=mag)
        picture.sample(1)
        os.remove(fileName)
        await ctx.followup.send(file=discord.File(glob(f"attachments/{safeFolder}/output/*")[0]))

    # Checks to see if the file's true format is correct
    except ValueError:
        await ctx.respond("Invalid file header.")

    except:
        await ctx.respond("Something strange has occured. Could not complete the request.")
        raise Exception

    # Deletes the temp folder and all files/folders in it
    if deleteOutput: rmtree(f"attachments/{safeFolder}")

# Polar Distortion command
@client.slash_command(name="polar", description="Distorts linked image into polar. Currently supports: png, jpg, jpeg.")
async def polar(ctx, imagelink: Option(str, "Insert a link of the photo you wish to distort.", required=False)):
    # Checks to see if a valid extension is being used
    if imagelink == None:
        messages = await ctx.channel.history(limit=5).flatten()
        messages.reverse()
        for msg in messages:
            # Checks to see if there are any images as attachments
            if (msg.attachments):
                for attachmentNumber in range(len(msg.attachments)):
                    if re.search(validUrl, str(msg.attachments[attachmentNumber])):
                        imagelink = (re.search(validUrl, str(msg.attachments[attachmentNumber]))).group(0)
                        break
                        
            #Checks to see if there are image links in text    
            if re.search(validUrl, msg.content):
                imagelink = (re.search(validUrl, msg.content)).group(0)
                break
                
        if imagelink == None:
            await ctx.respond("Could not locate a valid format in the past 5 messages.")
            return
        
    if imagelink[-3:] in ["png", "jpg"]:
        fileName = f"attachments/{gen_alpha(32) + imagelink[-4:]}"
    elif imagelink[-4:] in ["jpeg"]:
        fileName = f"attachments/{gen_alpha(32) + imagelink[-5:]}"
    else:
        await ctx.respond("Not a valid file or URL.")
        return

    # Downloads the file
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1")]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(imagelink, fileName)

    # Attempts to distort the image
    try:
        with Image(filename=fileName) as img:
            await ctx.respond("Distorting your image. One moment...")
            img.distort('polar', (0,))
            img.save(filename=fileName)
        await ctx.followup.send(file=discord.File(fileName))

    except ValueError:
        await ctx.respond("Invalid file header.")

    except:
        await ctx.respond("Something strange has occured. Could not complete the request.")

    #Removes the old file
    os.remove(fileName)

# Custom Commands
# use: Option(str, "Use a custom command.", required=False, default=False)
@custom.command(name="create", description="Create custom commands.")
async def create(ctx,
    name: Option(str, "Supply the name of the command.", required=True, default=False),
    action: Option(str, "Supply the desired output string.", required=True, default=False)):

    # Checks to see if create mode is on
    if name:
        # Valid length check
        if 1 <= len(name) <= 16:
            # Is action supplied?
            if action:
                # Is action length valid?
                if 1 <= len(action) <= 1750:
                    try:
                        # Checks if a command of that name exists in the server
                        sqlArgs = (ctx.guild.id, name)
                        commandSearch = sqlCursor.execute("SELECT command FROM servers WHERE server_id = ? AND command = ?", sqlArgs)
                        if commandSearch.fetchall():
                            await ctx.respond("A command with that name already exists! Please delete the command before proceeding with a new one.")
                            return

                        # Create and push the command
                        sqlArgs = (ctx.guild.id, name, action)
                        sqlCursor.execute("INSERT INTO servers VALUES (?, ?, ?)", sqlArgs)
                        sqlConn.commit()
                        await ctx.respond("Successfully created the custom command!")
                    except:
                        await ctx.respond("Something unexpected occured. Could not create command.")
                        raise Exception
            else:
                await ctx.respond("Action field required.")
        else:
            await ctx.respond("Invalid name length. Must be 1-16 characters in length!")

    else:
        await ctx.respond("Arguments required!")
   
@custom.command(name="use", description="Use custom commands.")
async def use(ctx,     
    command: Option(str, "Use a custom command.", required=True, default=False)):
    
    # Checks to see if the user is trying to use a custom command
    if command:
        try:
            # Pulls and prints the command. Checks to see if one exists of that name.
            sqlArgs = (ctx.guild.id, command)
            commandSearch = sqlCursor.execute("SELECT action FROM servers WHERE server_id = ? AND command = ?", sqlArgs)
            commandList = commandSearch.fetchall()
            await ctx.respond(str(commandList[0][0]))
            
        except:
            await ctx.respond("No valid commands found!")
            
    else:
        await ctx.respond("Arguments needed!")
        return

# Lists all custom commands on a server 
@custom.command(name="list", description="List custom commands created on the server.")
async def list(ctx):
    returnList = "Commands that currently exist on this server:\n"
    
    # Fetches all custom commands and prints them if available
    try:
        commandSearch = sqlCursor.execute(f"SELECT command FROM servers WHERE server_id = {ctx.guild.id}")
        commandList = commandSearch.fetchall()
        for commands in commandList:
            returnList += f"{commands[0]}\n"
        await ctx.respond(returnList)
        
    except:
        await ctx.respond("No commands found!")
        raise Exception

# Deletes custom commands on a server        
@custom.command(name="remove", description="Remove custom commands created on the server.")
async def remove(ctx,
    command: Option(str, "Use a custom command.", required=True, default=False)):
    
    # Checks to see if a command with the name exists - if not, deletes
    try:
        sqlArgs = (ctx.guild.id, command)
        commandSearch = sqlCursor.execute("DELETE FROM servers WHERE server_id = ? AND command = ?", sqlArgs)
        sqlConn.commit()
        await ctx.respond("Command successfully deleted!")
        
    except:
        await ctx.respond("No commands found!")
        raise Exception

# Main
if __name__ == "__main__":
    # Attempts to execute SQLite3. If it fails to do so, exits.
    try:
        print(f"Connecting with SQLite3 version {sqlite3.version}...")
        
        # Checks to see if database file exists
        if not(os.path.isfile("Jeremie.db")):
            databaseExists = False
            print("Jeremie.db file not found. Attempting to create a new database...")
        else:
            databaseExists = True
            print("Jeremie.db file found!")
        
        sqlConn = sqlite3.connect("Jeremie.db")
        sqlCursor = sqlConn.cursor()
        
        # If database file had to be created, this will add the correct tables
        if not(databaseExists):
            sqlCursor.execute("CREATE TABLE servers (server_id, command, action)")
            sqlCursor.execute("CREATE TABLE users (user_id, jeremites)")
            
    except:
        print("Could not connect to database. Terminating.")
        exit()
        
    print("Successfully connected!")

    # Makes a new attachments directory if ones does not exist
    if not(os.path.isdir("attachments")):
        print("Attachments directory not found. Creating new one.")
        os.mkdir("attachments")

    # Start the bot
    client.run(TOKEN)
