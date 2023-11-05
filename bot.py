import discord
import time
import datetime
import random
import typing
import os
import asyncio
import math
import json
from discord import Spotify
from discord.ext import commands

def get_prefix(bot, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

bot = commands.Bot(command_prefix= get_prefix)
token = 'your bot token'
bot.remove_command('help')
start_time = datetime.datetime.utcnow()

@bot.event
async def on_ready():
    print('-------') 
    print('Im Ready!')
    print(bot.user.name)
    print(bot.user.id)
    print('-------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(",help | ,invite"))
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print(f"Command not found on {ctx.guild} | Command executed by {ctx.message.author}({ctx.message.author.id})")

@bot.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = ','

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@bot.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@bot.event
async def on_message_delete(message):
    log_channel = discord.utils.get(message.guild.channels, name="deleted-messages")

    if not log_channel:
        channel = bot.get_channel()       #in () put your channel id!
        
        em = discord.Embed(title='Message deleted!', color=0xfcf8f8)
        em.add_field(name='Message Author:',value=f"{message.author.mention}(ID:{message.author.id})" or '\u200B',inline=False)
        em.add_field(name='Message Content:',value=f'{message.content}' or '\u200B',inline=False)
        em.add_field(name='Message Channel:',value=f'{message.channel.mention}' or '\u200B',inline=False)
        em.add_field(name='Server:',value=f"{message.guild}" or '\u200B',inline=False)
        em.set_footer(text='©Sparky')
        
        await channel.send(embed=em)

    else:
        e = discord.Embed(title='Message deleted!', color=0xfcf8f8)
        e.add_field(name='Message Author:',value=f"{message.author.mention}(ID:{message.author.id})" or '\u200B',inline=False)
        e.add_field(name='Message Content:',value=f"{message.content}" or '\u200B',inline=False)
        e.add_field(name='Channel:',value=f"{message.channel.mention}" or '\u200B',inline=False)
        e.set_footer(text='©Sparky')
            
        await log_channel.send(embed=e) 
        
@bot.command(name='stopbot')
@commands.is_owner()
async def stopbot(ctx):
    embed=discord.Embed(title=f"Hey {ctx.author}!", description=f"I am now logging out :wave:", color=0xfcf8f8)
    await ctx.send(embed=embed)
    await bot.logout()

@stopbot.error
async def stopbot_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed=discord.Embed(title="**Error**", description="You lack permission to use this command as you do not own the bot", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    else:
        raise error

@bot.command(name='change_prefix')
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 10, commands.BucketType.guild)
async def change_prefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    embed=discord.Embed(title=f"Successfully set the custom prefix", description=f"For {ctx.guild} the prefix has been set to: `{prefix}` .If you want to change it again, you have to wait 10 seconds.", color=0xfcf8f8)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)

@change_prefix.error
async def change_prefix_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description=f"Specify a prefix so I can set the custom prefix for this server: **{ctx.guild}**", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='logs_activate')
@commands.cooldown(1, 10, commands.BucketType.guild)
@commands.has_permissions(manage_channels = True)
async def log_activate(ctx):
    await ctx.guild.create_text_channel(name="deleted-messages")
    embed=discord.Embed(title="I have successfully activated the deleted messages channel", description="From now on, a message deleted by a member will appear on the created channel", color=0xfcf8f8)
    embed.set_footer(text='©Sparky')
    channe = discord.utils.get(ctx.guild.channels, name="deleted-messages")
    await ctx.send(embed=embed)
    em=discord.Embed(title="From now on I will send deleted messages here!", description=f"Channel: {channe.mention}({channe.id})", color=0xfcf8f8)
    em.add_field(name="Logs have been activated by:", value=f"{ctx.message.author.mention}", inline=False)
    embed.set_footer(text='©Sparky')
    await channe.send(embed=em)
        
@bot.command(name='ping')
async def ping(ctx):
    randomping = random.choice(['Poooong!','Poong!','Pong!','Pooong!'])
    embed = discord.Embed(title=f'**🏓{randomping}**', color=0xfcf8f8)
    embed.add_field(name='**Latency:**',value=f"{round(bot.latency * 1000)}ms📶",inline=False)
    embed.set_footer(text='©Sparky')
    await ctx.send(content=None, embed=embed)
    print(f'Bot Ping:{round(bot.latency * 1000)}ms') 
    
@bot.command(name='clear') 
@commands.cooldown(1, 3, commands.BucketType.guild)
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    embed=discord.Embed(title="**Done**", description="Messages have been deleted", color=0xfcf8f8)
    embed.set_footer(text='©Sparky') 
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} used command(clear) on {ctx.guild}") 

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      embed=discord.Embed(title="**Error**", description="Specify how many messages you want to delete", color=0xfcf8f8)
      embed.set_footer(text='©Sparky') 
      await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='support')
async def support(ctx):
    support_server = 'server invite link'
    description = f'''
    Join **[support server]({support_server})** for questions and support.
    '''
    embed=discord.Embed(title='Ask away!', description=description, color=0xfcf8f8)
    embed.set_footer(text='©Sparky') 
    await ctx.send(content=None, embed= embed)
    print(f"{ctx.message.author} wants support on {ctx.guild}")

@bot.command(name='invite')
async def invite(ctx):
    invite_link = 'put bot invite link'
    description = f'''
    Use this **[invite link]({invite_link})** to invite me.
    '''
    embed=discord.Embed(title='Invite Me :)', description=description, color=0xfcf8f8)
    embed.set_footer(text='©Sparky') 
    await ctx.send(content=None, embed= embed)
    print(f"{ctx.message.author} wants to invite Sparky on {ctx.guild}")

@bot.command(name='vote')
async def vote(ctx):
    vote_link = 'https://top.gg/bot/752202732902940783'
    description = f'''
    You can vote for me using this **[vote]({vote_link})**
    '''
    embed=discord.Embed(title='Vote Sparky:', description=description, color=0xfcf8f8)
    embed.set_footer(text='©Sparky') 
    await ctx.send(content=None, embed= embed)
    print(f"{ctx.message.author} wants to vote Scrappy on {ctx.guild}")
    
@bot.command(name='add_role')
@commands.cooldown(1, 2, commands.BucketType.guild)
@commands.has_permissions(manage_roles=True)
async def add_role(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    embed=discord.Embed(title="**Successfully added role**", description=f"**{role}** added to {member.mention}", color=0xfcf8f8)
    embed.set_footer(text='©Sparky') 
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} added {role} to {member} on {ctx.guild}")
    
@add_role.error
async def add_role_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(title="**Error**", description="I could not find that member...", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Say a member/role so I can add the role", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='remove_role')
@commands.cooldown(1, 2, commands.BucketType.guild)
@commands.has_permissions(manage_roles=True)
async def remove_role(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    embed=discord.Embed(title="**Successfully removed role**", description=f"**{role}** removed from {member.mention}", color=0xfcf8f8)
    embed.set_footer(text='©Sparky') 
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} removed {role} from {member} on {ctx.guild}")

@remove_role.error
async def remove_role_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(title="**Error**", description="I could not find that member...", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Say a member/role so I can remove the role", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='ban')
@commands.cooldown(1, 1, commands.BucketType.guild)
@commands.has_permissions(ban_members = True) 
async def ban(ctx, member : discord.Member, *, reason = None):
    await member.ban(reason = reason)
    embed=discord.Embed(title=f"**Successfully banned {member}**", color=0xfcf8f8)
    embed.add_field(name="**Responsible Moderator:**",value=f"{ctx.message.author}",inline=False)
    embed.add_field(name="**Member:**",value=f"{member}({member.id})",inline=False)
    embed.add_field(name="**Reason:**",value=f"{reason}",inline=False)
    embed.set_footer(text='©Sparky') 
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} banned {member} on {ctx.guild} | {reason}")

@ban.error
async def on_ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Please complete all requirements", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(title="**Error**", description="I could not find that member...", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='unban')
@commands.cooldown(1, 1, commands.BucketType.guild)
@commands.has_permissions(ban_members = True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            embed=discord.Embed(title=f"**Successfully unbanned {member}**", color=0xfcf8f8)
            embed.add_field(name="**Responsible Moderator:**",value=f"{ctx.message.author}",inline=False)
            embed.add_field(name="**Member:**",value=f"{member}( {member.id})",inline=False)
            embed.set_footer(text='©Sparky') 
            await ctx.send(embed=embed)
            print(f"{ctx.message.author} unbanned {member} on {ctx.guild}")

@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Please complete all requirements", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(title="**Error**", description="I could not find that member...", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='mute')
@commands.cooldown(1, 2, commands.BucketType.guild)
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: discord.Member = None, *, reason = None):
    role = discord.utils.get(ctx.guild.roles,  name="Muted")

    if role == None:

        role = await ctx.guild.create_role(name= "Muted", reason="Mute Role by Sparky")

    await member.add_roles(role)

    embed=discord.Embed(title=f"**Successfully muted {member}**",color=0xfcf8f8)
    embed.add_field(name="**Responsible Moderator:**",value=f"{ctx.message.author}",inline=False)
    embed.add_field(name="**Member:**",value=f"{member}({member.id})",inline=False)
    embed.add_field(name="**Reason:**",value=f"{reason}",inline=False)
    embed.set_footer(text='©Sparky')

    await ctx.send(embed=embed)
    print(f"{ctx.message.author} muted {member} in {ctx.guild} | {reason}")

    for channel in ctx.guild.channels:

        await channel.set_permissions(role , send_messages = False)

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Specifies a member or reason to mute him", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(title="**Error**", description="I could not find that member...", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='unmute')
@commands.cooldown(1, 2, commands.BucketType.guild)
@commands.has_permissions(kick_members=True)
async def unmute(ctx, member: discord.Member = None, *, reason=None):
    role = discord.utils.get(ctx.guild.roles,  name="Muted")

    await member.remove_roles(role)

    embed=discord.Embed(title=f"**Successfully unmuted {member}**",color=0xfcf8f8)
    embed.add_field(name="**Responsible Moderator:**",value=f"{ctx.message.author}",inline=False)
    embed.add_field(name="**Member:**",value=f"{member}({member.id})",inline=False)
    embed.add_field(name="**Reason:**",value=f"{reason}",inline=False)
    embed.set_footer(text='©Sparky')

    await ctx.send(embed=embed)
    print(f"{ctx.message.author} unmuted {member} in {ctx.guild} | {reason}")

@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Specifies a member or reason to unmute him", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(title="**Error**", description="I could not find that member...", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
        
@bot.command(name='kick')
@commands.cooldown(1, 2, commands.BucketType.guild)
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member=None , *, reason=None):
    if not member:
        embed=discord.Embed(title="**Error**", description="Specify a member so I can kick him", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
        return 
    await member.kick(reason=reason)
    embed=discord.Embed(title=f"**Successfully kicked {member}**",color=0xfcf8f8)
    embed.add_field(name="**Responsible Moderator:**",value=f"{ctx.message.author}",inline=False)
    embed.add_field(name="**Member:**",value=f"{member}({member.id})",inline=False)
    embed.add_field(name="**Reason:**",value=f"{reason}",inline=False)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} kicked {member} on {ctx.guild}")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Specify a member so I can kick him", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(title="**Error**", description="I could not find that member...", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='whois')
@commands.cooldown(1, 2, commands.BucketType.guild)
async def userinfo(ctx, member: discord.Member):
    embed = discord.Embed(title= f'{member}', color=0xfcf8f8)
    embed.add_field(name='**Username:**', value=member.name, inline=False)
    embed.add_field(name='**Discriminator:**', value=member.discriminator, inline=False)
    embed.add_field(name='**ID:**', value=member.id, inline=False)
    embed.add_field(name='**Status:**', value=member.status, inline=False)
    embed.add_field(name="**Highest Role:**", value=member.top_role, inline=False)
    embed.add_field(name='**Account Created:**', value=member.created_at.__format__('%A, %d. %B %Y | %H:%M:%S'), inline=False)
    embed.add_field(name='**Server Join Date:**', value=member.joined_at.__format__('%A, %d. %B %Y | %H:%M:%S'), inline=False)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text='©Sparky')
    await ctx.send(content=None, embed=embed)
    print(f"{ctx.message.author} found out some information about {member} on {ctx.guild}")

@userinfo.error
async def userinfo_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(title="**Error**", description="I could not find that member...", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Specify a member to tell you some information about him", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='serverinfo')
@commands.cooldown(1, 5, commands.BucketType.guild)
async def serverinfo(ctx):
    embed=discord.Embed(title=f'{ctx.guild.name}', color=0xfcf8f8)
    embed.set_thumbnail(url = ctx.message.guild.icon_url)
    embed.add_field(name='Server ID:',value=f"{ctx.guild.id}",inline=False)
    embed.add_field(name='Region:',value=f"{ctx.guild.region}",inline=False)
    embed.add_field(name='Verification Level:',value=f"{ctx.guild.verification_level}",inline=False)
    embed.add_field(name='Server Owner:',value=f"{ctx.guild.owner}",inline=False)
    embed.add_field(name='Server Created On:',value=ctx.guild.created_at.__format__('%A, %d. %B %Y | %H:%M:%S'),inline=False)
    embed.add_field(name='Number Of Member:',value=f"{ctx.guild.member_count}",inline=False)
    embed.add_field(name='Text Channels:',value=len(ctx.guild.text_channels),inline=False)
    embed.add_field(name='Voice Channels:',value=len(ctx.guild.voice_channels),inline=False)
    embed.add_field(name='Custom Emotes:',value=len(ctx.guild.emojis),inline=False)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)

@bot.command(name='slowmode')
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, amount):
    await ctx.channel.edit(reason='Bot Slowmode Command', slowmode_delay=int(amount))
    embed=discord.Embed(title="I successfully set the seconds for slowmode!", description=f"Slowmode for this channel was set to {amount} seconds",color=0xfcf8f8)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)

@slowmode.error
async def slowmode_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Specify a duration in seconds without putting **s** or anything else", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
        
        
@bot.command(name='uptime')
async def uptime(ctx: commands.Context):
    now = datetime.datetime.utcnow()
    delta = now - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    if days:
        time_format = "**{d}** days, **{h}** hours, **{m}** minutes, and **{s}** seconds."
    else:
        time_format = "**{h}** hours, **{m}** minutes, and **{s}** seconds."
    uptime_stamp = time_format.format(d=days, h=hours, m=minutes, s=seconds)
    embed=discord.Embed(title="Uptime", description=f"{bot.user.name} has been up for {uptime_stamp}", color=0xfcf8f8)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)
    print(f"{bot.user.name} has been up for {uptime_stamp}")

@bot.command(name='say')
@commands.cooldown(1, 1, commands.BucketType.user)
@commands.has_permissions(send_tts_messages = True)
async def echo(ctx, *, content):
    if ctx.message.mention_everyone:
        embed=discord.Embed(title="Error", description="Your message mentions everyone and I will not send it!", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    else:
        await ctx.send(content)
        await ctx.message.delete()
    print(f"{ctx.message.author} say <{content}> on {ctx.guild}")

@echo.error
async def echo_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Say a message so I can repeat it", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='square')
@commands.cooldown(1, 1, commands.BucketType.guild)
async def square(ctx, number):
    squared_value = int(number) * int(number)
    embed=discord.Embed(title="**Successfully squared number**", description=f"**{str(number)}** => **{str(squared_value)}**",color=0xfcf8f8)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} square {number} => {squared_value} on {ctx.guild}")

@square.error
async def square_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Say a number to square it", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='warn')
@commands.cooldown(1, 2, commands.BucketType.guild)
@commands.has_permissions(kick_members = True)
async def warn(ctx, member : discord.Member, *, question):
    embed = discord.Embed(title= f'{member} has been warned', color=0xfcf8f8)
    embed.add_field(name='**Member:**', value=f'{member}({member.id})', inline=False)
    embed.add_field(name='**Responsible Moderator:**', value=f'{ctx.author}', inline=False)
    embed.add_field(name='**Reason:**', value=f'{question}', inline=False)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} warned {member} on {ctx.guild} | {question}")

@warn.error
async def warn_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(title="**Error**", description="I could not find that member...", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Specify a member/reason to warn him", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='reply')
@commands.cooldown(1, 1, commands.BucketType.guild)
async def reply(ctx, *, question):
    responses = ["Yes" , "NO" , "Maybe" , "True" , "False"]
    embed=discord.Embed(title="My answer to the question", description=f"**{question}** is **{random.choice(responses)}**", color=0xfcf8f8)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} reply {question} on {ctx.guild}")

@reply.error
async def reply_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      embed=discord.Embed(title="**Error**", description="In order to be able to answer your question, you have to ask me a question", color=0xfcf8f8)
      embed.set_footer(text='©Sparky')
      await ctx.send(embed=embed)

@bot.command(name='about')
async def about(ctx):
    embed = discord.Embed(title= f'{bot.user.name}', color=0xfcf8f8)
    embed.add_field(name="**Developers:**", value="<@285130761860808704>", inline=True)
    embed.add_field(name="**Library:**", value="discord.py", inline=True)
    embed.add_field(name="**Servers:**", value=f"{str(len(bot.guilds))}", inline=True)
    embed.add_field(name="**Commands:**", value=f"{str(len(bot.commands))}", inline=True)
    embed.add_field(name="**Ping:**", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.set_footer(text='©Sparky')

    await ctx.send(embed=embed)
    print(f"{ctx.message.author} used command(about) on {ctx.guild}")

@bot.command(name="embed")
@commands.cooldown(1, 2, commands.BucketType.guild)
@commands.has_permissions(send_tts_messages = True)
async def embed(ctx, title, *, desc):
    embed = discord.Embed(title=title, description=desc, color=0xfcf8f8)
    embed.set_footer(text=f'©Sparky | Message Sent By {ctx.message.author}')
    await ctx.send(embed=embed)

@embed.error
async def embed_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Say a message so I can repeat it", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='avatar')
@commands.cooldown(1, 2, commands.BucketType.guild)
async def avatar(ctx, member: discord.Member=None):  
    if not member:
        member = ctx.message.author
    show_avatar = discord.Embed(title=f"{member}" ,description="[Avatar URL](%s)" % member.avatar_url, color=0xfcf8f8)
    show_avatar.set_image(url="{}".format(member.avatar_url))
    show_avatar.set_footer(text='©Sparky')
    await ctx.send(embed=show_avatar) 

@avatar.error
async def avatar_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Tell a member so I can show you his avatar", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(title="**Error**", description="I could not find that member...", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='hi')
async def hi(ctx):
    embed=discord.Embed(description=f"Hi {ctx.message.author.mention}!" ,color=0xfcf8f8)
    embed.set_footer(text='©Sparky') 
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} greeted himself on {ctx.guild}")

@bot.command(name='member_count')
@commands.cooldown(1, 5, commands.BucketType.guild)
async def member_count(ctx):
    embed=discord.Embed(title="Counting...", description=f"The server **{ctx.guild.name}** contains **{ctx.guild.member_count}** members", color=0xfcf8f8)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)

@bot.command(name='spotify')
async def spotify(ctx, user: discord.Member=None):
    user = user or ctx.author
    for activity in user.activities:
        if isinstance(activity, Spotify):
            description=f'''
            Song: **{activity.title}**
            Artist: **{activity.artist}**
            Album: **{activity.album}**
            '''
            embed=discord.Embed(title=f"{user} is listening to Spotify", description=description, color=0xfcf8f8)
            embed.set_footer(text='©Sparky')
            await ctx.send(embed=embed)
    print(f"{ctx.message.author} wants to know what {user} is listening to on Spotify")

@spotify.error
async def spotify_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(title="**Error**", description="I couldn't find that member...", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Tell a member to show you what they're listening to on Spotify", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='top_role')
async def top_role(ctx, *, member: discord.Member=None):
    embed=discord.Embed(title="Loading ..", description=f"The top role for {member.mention} in {ctx.guild} is: {member.top_role.name}", color=0xfcf8f8)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} wants to see the top role of {member} in {ctx.guild}")

@top_role.error
async def top_role(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(title="**Error**", description="I couldn't find that member...", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description=f"Tell a member so I can show you the highest role in {ctx.guild}", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='contact')
@commands.cooldown(1, 10, commands.BucketType.guild)
async def contact(ctx, *, question):
    embed = discord.Embed(title=f'Contacted by {ctx.message.author}', color=0xfcf8f8)
    embed.add_field(name="**Contacted by:**",value=f"{ctx.author.mention}",inline=False)
    embed.add_field(name="**Problem:**",value=f"{question}",inline=False)
    embed.set_footer(text='©Sparky')

    channel = bot.get_channel(752399228793520218)
    await channel.send(embed=embed)
    embed=discord.Embed(title="Successfully Contacted Owner|Developers|Support Team", description="You have successfully contacted the Owner, Developers and Sparky Support Team! You will receive the answer to the question in DM!",color=0xfcf8f8 )
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} contacted Owner/Support Team on {ctx.guild}")

@contact.error
async def contact_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="To contact the Owner / Support Team of the Scrappy bot you need to say a reason to receive the answer to the question", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='suggest')
@commands.cooldown(1, 30, commands.BucketType.guild)
async def suggest(ctx, *,suggestion):
    channel = bot.get_channel(752399229200236652)
    embed = discord.Embed(title=f'Suggestion by {ctx.message.author}', color=0xfcf8f8)
    embed.add_field(name="**Suggestion by:**",value=f"{ctx.author.mention}",inline=False)
    embed.add_field(name="**Suggest:**",value=f"{suggestion}",inline=False)
    embed.set_footer(text='©Sparky')

    await channel.send(embed=embed)
    embed=discord.Embed(title="Suggestion sent!", description="Your suggestion was sent to the developers of the **Sparky**! The suggestion will be analyzed and if it is good it will be added! Thanks for the suggestion!", color=0xfcf8f8)
    await ctx.send(embed=embed)

@suggest.error
async def suggest_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="To make a suggestion you must first write the suggestion", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='create_text_channel')
@commands.cooldown(1, 10, commands.BucketType.guild)
@commands.has_permissions(manage_channels = True)
async def create_text_channel(ctx, *, name):
    channel = await ctx.guild.create_text_channel(name=f"{name}")
    embed=discord.Embed(title="Successfully created the text channel", description=f"I created in **{ctx.guild}** the text channel named: **{name}** with ID: **{channel.id}**", color=0xfcf8f8)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} created a text channel:({name}) in {ctx.guild}")

@create_text_channel.error
async def create_text_channel_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Specify the channel name so I can create it", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='delete_text_channel')
@commands.cooldown(1, 10, commands.BucketType.guild)
@commands.has_permissions(manage_channels = True)
async def delete_text_channel(ctx, *, id:int):
    channel = bot.get_channel(id)
    await channel.delete()
    embed=discord.Embed(title="**Successfully deleted the text channel**", description=f"I deleted the text channel in **{ctx.guild}** with the name: **{channel.name}** and the ID: **{id}**", color=0xfcf8f8)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} deleted a text channel:({channel.name}) in {ctx.guild}")

@delete_text_channel.error
async def delete_text_channel_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Specify an ID of the channel you want to delete", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='create_role')
@commands.cooldown(1, 10, commands.BucketType.guild)
@commands.has_permissions(manage_roles = True)
async def create_role(ctx, *, name):
    role = await ctx.guild.create_role(name=f"{name}")
    embed=discord.Embed(title=f"Successfully created the role in {ctx.guild}", description=f"I created in **{ctx.guild}** a role named: **{name}** with ID: **{role.id}**", color=0xfcf8f8)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} created a role:({name}) in {ctx.guild}")

@create_role.error
async def create_role_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Specify a name for the role so I can create it", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name="delete_role", pass_context=True)
@commands.cooldown(1, 10, commands.BucketType.guild)
@commands.has_permissions(manage_roles = True)
async def delete_role(ctx, role_name):
    role_object = discord.utils.get(ctx.message.guild.roles, name=role_name)
    await role_object.delete()
    embed=discord.Embed(title=f"Successfully deleted role in {ctx.guild}", description=f"I deleted the role in **{ctx.guild}**", color=0xfcf8f8)
    embed.set_footer(text='©Sparky')
    await ctx.send(embed=embed)
    print(f"{ctx.message.author} deleted a role:({role_name}) in {ctx.guild}")

@delete_role.error
async def delete_role_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Specify the role name so that I can delete the role", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You don't have all the permissions", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='new')
@commands.cooldown(1, 2, commands.BucketType.guild)
async def new(ctx, *, args = None):

    await bot.wait_until_ready()

    if args == None:
        message_content = "Please wait, we will be with you shortly!"
    
    else:
        message_content = "".join(args)

    with open("data.json") as f:
        data = json.load(f)

    ticket_number = int(data["ticket-counter"])
    ticket_number += 1

    ticket_channel = await ctx.guild.create_text_channel("ticket-{}".format(ticket_number))
    await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False)

    for role_id in data["valid-roles"]:
        role = ctx.guild.get_role(role_id)

        await ticket_channel.set_permissions(role, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
    
    await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)

    em = discord.Embed(title="Hi {}#{}!".format(ctx.author.name, ctx.author.discriminator),description='**Our staff members will answer you soon!**', color=0xfcf8f8)
    em.add_field(name='**Problem:**',value=f"{message_content}",inline=False)
    em.set_footer(text='©Sparky')

    await ticket_channel.send(embed=em)

    pinged_msg_content = ""
    non_mentionable_roles = []

    if data["pinged-roles"] != []:

        for role_id in data["pinged-roles"]:
            role = ctx.guild.get_role(role_id)

            pinged_msg_content += role.mention
            pinged_msg_content += " "

            if role.mentionable:
                pass
            else:
                await role.edit(mentionable=True)
                non_mentionable_roles.append(role)
        
        await ticket_channel.send(pinged_msg_content)

        for role in non_mentionable_roles:
            await role.edit(mentionable=False)
    
    data["ticket-channel-ids"].append(ticket_channel.id)

    data["ticket-counter"] = int(ticket_number)
    with open("data.json", 'w') as f:
        json.dump(data, f)
    
    created_em = discord.Embed(title="I have successfully created your ticket!", description="Your ticket has been created at {}".format(ticket_channel.mention), color=0xfcf8f8)
    created_em.set_footer(text='©Sparky')
    
    await ctx.send(embed=created_em)

@bot.command(name='close')
@commands.cooldown(1, 1, commands.BucketType.guild)
async def close(ctx):
    with open('data.json') as f:
        data = json.load(f)

    if ctx.channel.id in data["ticket-channel-ids"]:

        channel_id = ctx.channel.id

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() == "close"

        try:

            em = discord.Embed(title="Do you really want to close this ticket?", description="Are you sure you want to close this ticket? Reply with `close` if you are sure.", color=0xfcf8f8)
            em.set_footer(text='©Sparky')
        
            await ctx.send(embed=em)
            await bot.wait_for('message', check=check, timeout=60)
            await ctx.channel.delete()

            index = data["ticket-channel-ids"].index(channel_id)
            del data["ticket-channel-ids"][index]

            with open('data.json', 'w') as f:
                json.dump(data, f)
        
        except asyncio.TimeoutError:
            em = discord.Embed(title="The waiting time is up", description="You have run out of time to close this ticket. Please run the command again.", color=0xfcf8f8)
            em.set_footer(text='©Sparky')
            await ctx.send(embed=em)

@bot.command(name='addaccess')
@commands.cooldown(1, 2, commands.BucketType.guild)
async def addaccess(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:
        role_id = int(role_id)

        if role_id not in data["valid-roles"]:

            try:
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                data["valid-roles"].append(role_id)

                with open('data.json', 'w') as f:
                    json.dump(data, f)
                
                em = discord.Embed(title="Role successfully added", description="You have successfully added `{}` to the list of roles with access to tickets.".format(role.name), color=0xfcf8f8)
                em.set_footer(text='©Sparky')

                await ctx.send(embed=em)

            except:
                em = discord.Embed(title="Error", description="That isn't a valid role ID. Please try again with a valid role ID.", color=0xfcf8f8)
                em.set_footer(text='©Sparky')
                await ctx.send(embed=em)
        
        else:
            em = discord.Embed(title="Error", description="That role already has access to tickets!", color=0xfcf8f8)
            em.set_footer(text='©Sparky')
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="Error", description="Sorry, you don't have permission to run that command.", color=0xfcf8f8)
        em.set_footer(text='©Sparky')
        await ctx.send(embed=em)

@bot.command(name='delaccess')
@commands.cooldown(1, 3, commands.BucketType.guild)
async def delaccess(ctx, role_id=None):
    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass

    if valid_user or ctx.author.guild_permissions.administrator:

        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            valid_roles = data["valid-roles"]

            if role_id in valid_roles:
                index = valid_roles.index(role_id)

                del valid_roles[index]

                data["valid-roles"] = valid_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="Successfully removed role", description="You have successfully removed `{}` from the list of roles with access to tickets.".format(role.name), color=0xfcf8f8)
                em.set_footer(text='©Sparky')
                await ctx.send(embed=em)
            
            else:
                
                em = discord.Embed(title="Error", description="That role already doesn't have access to tickets!", color=0xfcf8f8)
                em.set_footer(text='©Sparky')
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="Error", description="That isn't a valid role ID. Please try again with a valid role ID.", color=0xfcf8f8)
            em.set_footer(text='©Sparky')
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="Error", description="Sorry, you don't have permission to run that command.", color=0xfcf8f8)
        em.set_footer(text='©Sparky')
        await ctx.send(embed=em)

@bot.command(name='addpingedrole')
@commands.cooldown(1, 2, commands.BucketType.guild)
async def addpingedrole(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:

        role_id = int(role_id)

        if role_id not in data["pinged-roles"]:

            try:
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                data["pinged-roles"].append(role_id)

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="Role successfully added", description="You have successfully added `{}` to the list of roles that get pinged when new tickets are created!".format(role.name), color=0xfcf8f8)
                em.set_footer(text='©Sparky')
                await ctx.send(embed=em)

            except:
                em = discord.Embed(title="Error", description="That isn't a valid role ID. Please try again with a valid role ID.", color=0xfcf8f8)
                em.set_footer(text='©Sparky')
                await ctx.send(embed=em)
            
        else:
            em = discord.Embed(title="Error", description="That role already receives pings when tickets are created.", color=0xfcf8f8)
            em.set_footer(text='©Sparky')
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="Error", description="Sorry, you don't have permission to run that command.", color=0xfcf8f8)
        em.set_footer(text='©Sparky')
        await ctx.send(embed=em)

@bot.command(name='delpingedrole')
@commands.cooldown(1, 3, commands.BucketType.guild)
async def delpingedrole(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:

        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            pinged_roles = data["pinged-roles"]

            if role_id in pinged_roles:
                index = pinged_roles.index(role_id)

                del pinged_roles[index]

                data["pinged-roles"] = pinged_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="Successfully removed role", description="You have successfully removed `{}` from the list of roles that get pinged when new tickets are created.".format(role.name), color=0xfcf8f8)
                em.set_footer(text='©Sparky')
                await ctx.send(embed=em)
            
            else:
                em = discord.Embed(title="Error", description="That role already isn't getting pinged when new tickets are created!", color=0xfcf8f8)
                em.set_footer(text='©Sparky')
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="Error", description="That isn't a valid role ID. Please try again with a valid role ID.", color=0xfcf8f8)
            em.set_footer(text='©Sparky')
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="Error", description="Sorry, you don't have permission to run that command.", color=0xfcf8f8)
        em.set_footer(text='©Sparky')
        await ctx.send(embed=em)

@bot.command(name='addadminrole')
@commands.cooldown(1, 2, commands.BucketType.guild)
@commands.has_permissions(administrator=True)
async def addadminrole(ctx, role_id=None):

    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)

        with open("data.json") as f:
            data = json.load(f)

        data["verified-roles"].append(role_id)

        with open('data.json', 'w') as f:
            json.dump(data, f)
        
        em = discord.Embed(title="Role successfully added", description="You have successfully added `{}` to the list of roles that can run admin-level commands!".format(role.name), color=0xfcf8f8)
        em.set_footer(text='©Sparky')
        await ctx.send(embed=em)

    except:
        em = discord.Embed(title="Error", description="That isn't a valid role ID. Please try again with a valid role ID.", color=0xfcf8f8)
        em.set_footer(text='©Sparky')
        await ctx.send(embed=em)

@bot.command(name='deladminrole')
@commands.cooldown(1, 3, commands.BucketType.guild)
@commands.has_permissions(administrator=True)
async def deladminrole(ctx, role_id=None):
    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)

        with open("data.json") as f:
            data = json.load(f)

        admin_roles = data["verified-roles"]

        if role_id in admin_roles:
            index = admin_roles.index(role_id)

            del admin_roles[index]

            data["verified-roles"] = admin_roles

            with open('data.json', 'w') as f:
                json.dump(data, f)
            
            em = discord.Embed(title="Successfully removed role", description="You have successfully removed `{}` from the list of roles that get pinged when new tickets are created.".format(role.name), color=0xfcf8f8)
            em.set_footer(text='©Sparky')
            await ctx.send(embed=em)
        
        else:
            em = discord.Embed(title="Error", description="That role isn't getting pinged when new tickets are created!", color=0xfcf8f8)
            em.set_footer(text='©Sparky')
            await ctx.send(embed=em)

    except:
        em = discord.Embed(title="Error", description="That isn't a valid role ID. Please try again with a valid role ID.", color=0xfcf8f8)
        em.set_footer(text='©Sparky')
        await ctx.send(embed=em)

@bot.command(name='poll')
@commands.has_permissions(manage_messages=True)
@commands.cooldown(1, 10, commands.BucketType.guild)
async def poll(ctx, *,polldesc):
    embed=discord.Embed(title="📢 POLL", description=f"{polldesc}", color=0xfcf8f8)
    embed.set_footer(text=f'©Sparky | Poll created by: {ctx.message.author}')
    msg=await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    await ctx.message.delete()
    print(f"{ctx.message.author} created a poll in {ctx.guild} | {polldesc}")

@poll.error
async def poll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title="**Error**", description="Specifies a poll message", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)
    if isinstance(error, commands.MissingPermissions):
        embed=discord.Embed(title="**Error**", description="You do not have all the permissions to create a poll", color=0xfcf8f8)
        embed.set_footer(text='©Sparky')
        await ctx.send(embed=embed)

@bot.command(name='help') 
@commands.cooldown(1, 1, commands.BucketType.guild)
async def help(ctx):
    embed = discord.Embed(title=f'**Help:**', color=0xfcf8f8)
    embed.add_field(name='**💼Role Management:**',value="`,add_role <@user> <@role>` | `,remove_role <@user> <@role>` | `,create_role <role-name>` | `,delete_role <role-name>`",inline=False)
    embed.add_field(name='**🛡️Moderation:**',value="`,change_prefix <new-prefix>` |`,ban <@user> <reason>` | `,unban <user#1234> <reason>` | `,mute <@user> <reason>` | `,unmute <@user> <reason>` | `,kick <@user>` | `,warn <@user> <reason>` | `,clear <limit>` | `,whois <@user>` | `,logs_activate`",inline=False)
    embed.add_field(name='**🗺️Utility:**',value="`,change_prefix <custom-prefix>` | `,serverinfo` | `,contact <problem>` | `,support` | `,ping` | `,about` | `,invite` | `,uptime` | `,vote` | `,slowmode <seconds>` | `,embed <title> <description>` | `,avatar <@user>` | `,member_count` | `,top_role <@user>` | `,suggest <suggestion>` | `,poll <poll-message>`",inline=False)
    embed.add_field(name='**📜Channels:**',value="`,create_text_channel <name>` | `,delete_text_channel <channel-id>`",inline=False)
    embed.add_field(name='**🎫Tickets:**',value="`,new <problem>` | `,close` | `,addaccess <role-id>` | `,delaccess <role-id>` | `,addadminrole <role-id>` | `,deladminrole <role-id>` | `,addpingedrole <role-id>` | `,delpingedrole <role-id>`",inline=False)
    embed.add_field(name='**👻Fun:**',value="`,square <number>` | `,reply <message>` | `,hi` | `,spotify <@user>` | `,say <message>`",inline=False)
    embed.set_footer(text='©Sparky') 
    await ctx.send(content=None, embed=embed)
    print(f"{ctx.message.author} wants to know the commands of the Sparky on {ctx.guild}")

bot.run(token)
