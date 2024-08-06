import os
from datetime import datetime

import discord
from discord.ext import commands, tasks
import dotenv

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

member_stream_start_times = {}
guild_leaderboards = {}

FIRST_DAY_OF_MONTH = 1

def calculateTimeWorked(seconds):
    hours = seconds // 3600
    minutes = (seconds // 60) % 60
    seconds = seconds % 60
    return f'{hours}h:{minutes}m:{seconds}s'

def clear_all_leaderboards():
    for guild_id in guild_leaderboards.keys():
        guild_leaderboards[guild_id] = {}

@bot.event
async def on_ready():
    if bot.user is None:
        return
    print(f'{bot.user.name} has connected to Discord!\n')
    date_checker.start()

@bot.event
async def on_guild_join(guild : discord.Guild):
    guild_leaderboards[guild.id] = dict()
    print("GuildId To Leaderboard has been initialised")

@bot.event
async def on_voice_state_update(member : discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if before.self_stream == False and after.self_stream == True:
        print("a pornit stream-ul")
        member_stream_start_times[member.id] = datetime.now()
    elif before.self_stream == True and (after.self_stream == False or member.voice is None):
        print("a oprit stream-ul")
        stop_time = datetime.now()
        start_time = member_stream_start_times.pop(member.id, stop_time)
        delta = stop_time - start_time
        seconds_worked = delta.seconds

        guild_leaderboard = guild_leaderboards.setdefault(member.guild.id, {})
        guild_leaderboard[member.id] = guild_leaderboard.get(member.id, 0) + seconds_worked

        await member.guild.text_channels[2].send(f'<@{member.id}> has worked for {calculateTimeWorked(seconds_worked)}!')


@bot.command(name="leaderboard")
async def show_leaderboard(ctx: commands.Context):
    guild = ctx.guild
    author = ctx.message.author

    if guild is None:
        return
    
    print('Leaderboard: Guild exists!')

    leaderboard = guild_leaderboards.get(guild.id, {})
    if not leaderboard:
        await ctx.message.channel.send(f'Leaderboard is empty!')
        return
    
    print('Leaderboard: guild\'s leaderboard exists')

    sorted_leaderboard = sorted(guild_leaderboards[guild.id].items(), key=lambda item: item[1], reverse=True)

    message = "Top 3 members by time worked:\n"

    for i, (member_id, seconds_worked) in enumerate(sorted_leaderboard[:3]):
        member = await bot.fetch_user(member_id)
        print(f'{member_id} + {seconds_worked}\nMember: {member}')
        if member:
            message += f'{i+1}. {member.name} has worked: {calculateTimeWorked(seconds_worked)}\n'

    if author.id in leaderboard:
        print('Author exists already on leaderboard')

        author_place = next((i + 1 for i, (member_id, _) in enumerate(sorted_leaderboard) if member_id == author.id))
        author_seconds_worked = leaderboard[author.id]

        message += f'\n<@{author.id}> is on {author_place}/{len(sorted_leaderboard)} position and has worked: {calculateTimeWorked(author_seconds_worked)}!'

    else:
        print('Author doesn\'t exist in leaderboard')

        message += f'\n<@{author.id}> isn\'t on leaderboard :('

    await ctx.send(message)

@tasks.loop(hours=24)
async def date_checker():
    print("Running date checker...")

    if datetime.now().day == FIRST_DAY_OF_MONTH:
        print("entered if!!!")
        clear_all_leaderboards()

@date_checker.before_loop
async def before_date_checker():
    print('waiting...')
    await bot.wait_until_ready()

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

if TOKEN is not None:
    bot.run(TOKEN)