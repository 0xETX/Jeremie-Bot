#===NOTE===
#Wand may require either of the packages below to be installed
#Windows: https://imagemagick.org/script/download.php#windows, https://docs.wand-py.org/en/0.6.2/guide/install.html
#Linux (Debian): apt-get install libmagickwand-dev
import os
import discord
import re
import asyncio
import random
import subprocess
import urllib.request
import Augmentor
import sqlite3
from shutil import rmtree
from time import sleep
from dotenv import load_dotenv
from discord.ext import commands
from discord.commands import Option
from threading import Thread
from glob import glob
from wand.image import Image
from wand.display import display

#Env token loading
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Bot Strings
prefix = "jc!"
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix = prefix, intents=intents)

#Variables
alphanumeric = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

#Prints if bot successfully runs
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

#Ping Command
@client.slash_command(name="ping", description="The bot pings the server to check response time. The lower, the faster the response.")
async def ping(ctx):
    await ctx.respond(f"{ctx.author.mention}, Jeremie has arrived. `({round(client.latency*1000)}ms)`")

#Custom Commands
@client.slash_command(name="custom", description="Create or use custom commands.")
async def custom(ctx,
    create: Option(str, "Create a custom command. Supply the name of the command.", required=False, default=False),
    action: Option(str, "Supply the desired output string.", required=False, default=False),
    use: Option(str, "Use a custom command.", required=False, default=False)):
    
    #Checks to see if create mode is on
    if (create):
        #Valid length check
        if 1 <= len(create) <= 16:
            #Is action supplied?
            if (action):
                #Is action length valid?
                if 1 <= len(action) <= 1750:
                    try:
                        #Checks if a command of that name exists in the server
                        sqlArgs = (ctx.guild.id, create)
                        commandSearch = sqlCursor.execute("SELECT command FROM servers WHERE server_id = ? AND command = ?", sqlArgs)
                        if commandSearch.fetchall():
                            await ctx.respond("A command with that name already exists! Please delete the command before proceeding with a new one.")
                            return
                        
                        #Create and push the command
                        sqlArgs = (ctx.guild.id, create, action)
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
     
    #Checks to see if the user is trying to use a custom command
    elif (use):
        try:
            #Pulls and prints the command. Checks to see if one exists of that name.
            sqlArgs = (ctx.guild.id, use)
            commandSearch = sqlCursor.execute("SELECT action FROM servers WHERE server_id = ? AND command = ?", sqlArgs)
            if commandSearch:
                await ctx.respond(str(commandSearch.fetchall()[0])[2:-3])
            else:
                await ctx.respond("No valid commands found!")
        except:
            await ctx.respond("An unexpected error has occured!")
            raise Exception
        
    else:
        await ctx.respond("Arguments required!")
        
#Distort Command   
@client.slash_command(name="distort", description="Distorts linked images into random directions. Currently supports: png, jpg, jpeg.")
async def distort(ctx, 
    imagelink: Option(str, "Insert a link of the photo you wish to distort.", required=True), 
    magnitude: Option(int, "Intensity of distortion. Recommended settings are -50 to 50.", required=False)):
    
    #Create temp folder name
    safeFolder = f"{(''.join(random.choice(alphanumeric) for i in range(32)))}"
    
    #Sees if magnitude is valid
    try:
        mag = int(magnitude)
    except:
        mag = random.randint(25,30)
        
    #Checks if extension is valid
    if (imagelink[-3:] in ["png", "jpg"]):
        fileName = f"attachments/{safeFolder}/{(''.join(random.choice(alphanumeric) for i in range(32)))+ imagelink[-4:]}"
    elif(imagelink[-4:] in ["jpeg"]):
        fileName = f"attachments/{safeFolder}/{(''.join(random.choice(alphanumeric) for i in range(32)))+ imagelink[-5:]}"
    else:
        await ctx.respond("Not a valid file or URL.")
        return
    
    #Creates a new folder and downloads image
    os.mkdir(f"attachments/{safeFolder}")
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1")]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(imagelink, fileName)
        
    #Attempts to distort and send the image
    try:    
        await ctx.respond("Distorting your image. One moment...")
        p = Augmentor.Pipeline(r"attachments/"+safeFolder)
        p.crop_random(probability=1, percentage_area=0.9)
        p.random_distortion(probability=1, grid_width=random.randint(4,7), grid_height=random.randint(8,12), magnitude=mag)
        p.sample(1)
        os.remove(fileName)
        await ctx.followup.send(file=discord.File(glob(f"attachments/{safeFolder}/output/*")[0]))
     
    #Checks to see if the file's true format is correct
    except ValueError:
        await ctx.respond("Invalid file header.")
        
    except:
        await ctx.respond("Something strange has occured. Could not complete the request.")
        raise Exception
        
    #Deletes the temp folder and all files/folders in it
    rmtree(f"attachments/{safeFolder}")
        
#Polar Distortion command
@client.slash_command(name="polar", description="Distorts linked image into polar. Currently supports: png, jpg, jpeg.")
async def polar(ctx, imagelink: Option(str, "Insert a link of the photo you wish to distort.", required=True)):
    #Checks to see if a valid extension is being used
    if (imagelink[-3:] in ["png", "jpg"]):
        fileName = f"attachments/{(''.join(random.choice(alphanumeric) for i in range(32)))+ imagelink[-4:]}"
    elif(imagelink[-4:] in ["jpeg"]):
        fileName = f"attachments/{(''.join(random.choice(alphanumeric) for i in range(32)))+ imagelink[-5:]}"
    else:
        await ctx.respond("Not a valid file or URL.")
        return
    
    #Downloads the file
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1")]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(imagelink, fileName)
        
    #Attempts to distort the image
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

#TBD if used or not
#@client.command(brief="Random dog image", description="The bot will send a random image of a dog.", commands_heading="Fun")
#async def dog(ctx):
#    cwd = os.getcwd() + "\\Dog"
#    randfile = random.choice(os.listdir(cwd))
#    await ctx.respond(file=discord.File(cwd+"\\"+randfile))
        
#Main
if __name__ == "__main__":      
    #Attempts to execute SQLite3. If it fails to do so, exits.
    try:
        print(f"Connecting with SQLite3 version {sqlite3.version}...")
        sqlConn = sqlite3.connect("Jeremie.db")
        sqlCursor = sqlConn.cursor()
        print("Successfully connected!")
    except:
        print("Could not connect to database. Terminating.")
        exit()
        
    #Makes a new attachments directory if ones does not exist
    if not(os.path.isdir("attachments")):
        print("Attachments directory not found. Creating new one.")
        os.mkdir("attachments")
       
    #Start the bot
    client.run(TOKEN)
