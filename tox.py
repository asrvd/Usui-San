import discord
from discord.ext import commands
import os
import asyncio
import json
from decouple import config
import os
import pyrebase

token = config("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.presences = True
MUTED_ROLE_ID = 785030970050740236
GUILD_ID = 785024897863647282
user_db = []

firebase = pyrebase.initialize_app(json.loads(config("firebaseConfig")))
db = firebase.database()

def create(user: int):
  db.child("DETOX_USER").child(user).set(
        {"DETOX": "True"}
  )

def check(user: int):
  member = db.child("DETOX_USER").child(user).get().val()
  if member == None:
    return False
  else:
    return True  

def remove(user: int):
  db.child("DETOX_USER").child(user).remove()    

ver_user=[
  666578281142812673,
  784363251940458516,
  443844596586250240,
  695870470045696020,
  735065640456683591,
  801995428044079134
]

client = commands.Bot(command_prefix='t.', case_insensitive=True, intents=intents)
client.remove_command("help")


@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.online, activity=discord.Game('With Miko Chan'))
  print('Bot is Online.')  

@client.command()
async def help(ctx):
    h = discord.Embed(
      title="NEED HELP?",
      description="Bot Creator: **ASHISH**",
      color=0x13fc03,
    )
    h.add_field(
      name="__ABOUT__", 
      value=f"\nPrefix : `t.`\nTox Kun is a Discord Bot created to help people complete a detox effectively. You can start your detox timer using Tox Kun and Tox Kun will change your nickname to `[DETOX]user` and will mute you from the server for the time given.", 
      inline=False
    )
    h.add_field(
      name="__HOW TO USE__",
      value=f"The time specified should be atleast in hours or Tox Kun will not work. Here is how to use the command: `t.detox 1h`. This will start a detox timer for 1 hour. To start detox for days use `d` in place of `h` like `t.detox 1d` will start a detox timer for 1 day.",
      inline=False
    )
    h.add_field(
      name="__COMMANDS__",
      value=f"`detox (time)` Starts detox timer for the user.\n`stop (user)` This command can be used only by me, admins or the mods. It stops the detox timer for the user.",
      inline=False
    )
    h.add_field(
      name="__TO STOP TIMER__",
      value=f"In case you accidently started a detox or want to stop your detox timer, you can either contact `me`, `admin` or the `mods`.",
      inline=False
    )

    await ctx.send(embed=h)

@client.command()
async def source(ctx):
  await ctx.send("https://replit.com/@AshKun/tox-chan")  


@client.command()
async def detox(ctx, time=None):
  if not time:
    await ctx.send("You must mention a time!")
  else:
    member = ctx.author  
    old_nick = member.display_name
    new_nick = "[DETOX]" + old_nick
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    time_convert = {"m": 60,"h":3600,"d":86400}
    if time[-1] == "h" or time[-1] == "d" or time[-1] == "m":
      tempmute= int(time[:-1]) * time_convert[time[-1]]
      await member.edit(nick=new_nick)
      await member.add_roles(role)
      create(ctx.author.id)
      detox_embed = discord.Embed(title="Your detox starts now!", description=f"{member.mention} is on detox for {time}\nGood Luck!", color=0x13fc03)
      await ctx.send(embed=detox_embed)
      await asyncio.sleep(tempmute)
      if check(ctx.author.id) == True:
        await member.remove_roles(role)
        undetox_embed = discord.Embed(title="Your detox has ended!", description=f"{member.mention} you were on detox for {time}\nGreat work!", color=0x13fc03)
        await ctx.send(embed=undetox_embed)
        await member.edit(nick=old_nick)
        remove(ctx.author.id)
      else:
        return  
    else:
      await ctx.send(f"{ctx.author.mention}Would that even be considered a detox?") 
            

@client.command()
async def stop(ctx, member: discord.Member):
  role = discord.utils.get(ctx.guild.roles, name="Muted")
  if ctx.author.id in ver_user:
    if check(member.id) == True:
      nick = member.display_name
      new_nick = nick[7:]
      await member.remove_roles(role)
      await member.edit(nick=new_nick)
      remove(member.id)
      undetox_embed = discord.Embed(title="Your detox timer has been stopped!", description=f"{member.mention} you are not on detox now.", color=0x13fc03)
      await ctx.send(embed=undetox_embed)
    else:
      await ctx.send("The specified user is not on detox currently.")  
  else:
    await ctx.send(f"{ctx.author.mention} You do not have permission to use this command!")    

@client.event
async def on_message(message):
  await client.process_commands(message)
  if message.author.bot:
    return
  for mention in message.mentions:
    if check(mention.id) == True:
      await message.channel.send(
        f"{message.author.mention}, **{mention}** is on DETOX! Do not ping them!", delete_after=25,)

client.run(token)     
 
