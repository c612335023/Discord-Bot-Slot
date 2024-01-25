import discord
from discord.ext import commands
import random
import json
import asyncio
import os

token = "MTE4MjYzNTc1NzU2MzgxODAyNA.GMTk4W.9JFfq59q3t1oEeambGxfFy97OKU-tVl7-nBPYI"

bot = commands.Bot(
    command_prefix='$',
    case_insensitive=True,
    help_command=None,
    activity=discord.Game("Slot"),
    intents=discord.Intents.all()
)

multipliers = {
    ':seven:': 50,
    ':chocolate_bar:': 30,
    ':bell:': 10,
    ':tangerine:': 5,
    ':lemon:': 3,
    ':grapes:': 2
}

@bot.event
async def on_ready():
    print('ログインしました')

def money_check(user_id):
    with open(f'{user_id}.json', 'r') as f:
        data = json.load(f)
    return data['money']

def update_money(user_id, amount):
    with open(f'{user_id}.json', 'r+') as f:
        data = json.load(f)
        data['money'] += amount
        f.seek(0)
        json.dump(data, f)
        f.truncate()

def update_bonus(user_id, update=False):
    with open(f'{user_id}.json', 'r+') as f:
        data = json.load(f)
        data['bonus'] += 1
        if update:
            data['bonus'] = 0
        f.seek(0)
        json.dump(data, f)
        f.truncate()
    return data['bonus']

def update_chance(user_id, chance=0):
    with open(f'{user_id}.json', 'r+') as f:
        data = json.load(f)
        data['chance'] += chance
        f.seek(0)
        json.dump(data, f)
        f.truncate()
    return data['chance']

slot_list = [':seven:', ':chocolate_bar:', ':bell:', ':tangerine:', ':lemon:', ':grapes:', ':cherries:']
w = [1,2,4,8,16,32,10]

@bot.command()
async def help(ctx):
    await ctx.send("$slot [賭け金] [回数]")

@bot.command()
async def slot(ctx, stake: int, count=0):
    author_id = ctx.author.id
    if count == 0:
        if not os.path.exists(f'{author_id}.json'):
            with open(f'{author_id}.json', 'w') as f:
                author = ctx.author
                json.dump({'author': str(author), 'money': 100, 'bonus': 0, 'chance': 0}, f)

        if ctx.author.voice is None:
            await ctx.send("あなたはボイスチャンネルに参加していません")
            return
        if ctx.guild.voice_client is None:
            await ctx.author.voice.channel.connect()

        user_money = money_check(author_id)
        if user_money < stake:
            await ctx.send("お金が足りません")
            return

        update_money(author_id, -stake)
        await ctx.send(f"持ち金：{user_money - stake}({user_money} - {stake})")

        results = random.choices(slot_list, k=5, weights=w)

        prob = update_bonus(author_id)
        if random.randint(1, 100) == prob:
            update_bonus(author_id, True)
            await ctx.send("ボーナス確定！")
            results[1:4] = [':seven:', ':seven:', ':seven:']

        for result in results:
            ctx.guild.voice_client.play(
                discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("ガコッ.wav"), volume=0.1)
            )
            await ctx.send(result)
            await asyncio.sleep(0.75)

        if all(result == results[0] for result in results):
            if results[0] == ':cherries:':
                update_chance(author_id, 30)
                await ctx.send("報酬2倍！（+30回）")
                multiplier = 0
            else:
                multiplier = multipliers.get(results[0], 0) * 10
        elif any(results[i] == results[i+1] == results[i+2] == results[i+3] for i in range(0,2)):
            if results[1] == ':cherries:':
                update_chance(author_id, 20)
                await ctx.send("報酬2倍！（+20回）")
                multiplier = 0
            else:
                multiplier = multipliers.get(results[1], 0) * 5
        elif any(results[i] == results[i+1] == results[i+2] for i in range(0,3)):
            if results[2] == ':cherries:':
                update_chance(author_id, 10)
                await ctx.send("報酬2倍！（+10回）")
                multiplier = 0
            else:
                multiplier = multipliers.get(results[2], 0)
        else:
            multiplier = 0

        if update_chance(author_id) > 0:
            update_money(author_id, stake * multiplier * 2)
            await ctx.send(f"獲得金額：{stake * multiplier * 2}({stake} × {multiplier} × 2)")
            await ctx.send(f"現在の持ち金：{money_check(author_id)}")
            update_chance(author_id, -1)
        else:
            update_money(author_id, stake * multiplier)
            await ctx.send(f"獲得金額：{stake * multiplier}({stake} × {multiplier})")
            await ctx.send(f"現在の持ち金：{money_check(author_id)}")
        await ctx.send("------------------------------")
    else:
        for i in range(count):
            if not os.path.exists(f'{author_id}.json'):
                with open(f'{author_id}.json', 'w') as f:
                    author = ctx.author
                    json.dump({'author': str(author), 'money': 100, 'bonus': 0, 'chance': 0}, f)

            if ctx.author.voice is None:
                await ctx.send("あなたはボイスチャンネルに参加していません")
                return
            if ctx.guild.voice_client is None:
                await ctx.author.voice.channel.connect()

            user_money = money_check(author_id)
            if user_money < stake:
                await ctx.send("お金が足りません")
                return

            await ctx.send(f"{i+1}回目")

            update_money(author_id, -stake)
            await ctx.send(f"持ち金：{user_money - stake}({user_money} - {stake})")

            results = random.choices(slot_list, k=5, weights=w)

            prob = update_bonus(author_id)
            if random.randint(1, 100) == prob:
                update_bonus(author_id, True)
                await ctx.send("ボーナス確定！")
                results[1:4] = [':seven:', ':seven:', ':seven:']

            for result in results:
                ctx.guild.voice_client.play(
                    discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("ガコッ.wav"), volume=0.1)
                )
                await ctx.send(result)
                await asyncio.sleep(0.75)

            if all(result == results[0] for result in results):
                if results[0] == ':cherries:':
                    update_chance(author_id, 30)
                    await ctx.send("報酬2倍！（+30回）")
                    multiplier = 0
                    break
                else:
                    multiplier = multipliers.get(results[0], 0) * 10
            elif any(results[i] == results[i+1] == results[i+2] == results[i+3] for i in range(0,2)):
                if results[1] == ':cherries:':
                    update_chance(author_id, 20)
                    await ctx.send("報酬2倍！（+20回）")
                    multiplier = 0
                    break
                else:
                    multiplier = multipliers.get(results[1], 0) * 5
            elif any(results[i] == results[i+1] == results[i+2] for i in range(0,3)):
                if results[2] == ':cherries:':
                    update_chance(author_id, 10)
                    await ctx.send("報酬2倍！（+10回）")
                    multiplier = 0
                    break
                else:
                    multiplier = multipliers.get(results[2], 0)
            else:
                multiplier = 0

            if update_chance(author_id) > 0:
                update_money(author_id, stake * multiplier * 2)
                await ctx.send(f"獲得金額：{stake * multiplier * 2}({stake} × {multiplier} × 2)")
                await ctx.send(f"現在の持ち金：{money_check(author_id)}")
                update_chance(author_id, -1)
            else:
                update_money(author_id, stake * multiplier)
                await ctx.send(f"獲得金額：{stake * multiplier}({stake} × {multiplier})")
                await ctx.send(f"現在の持ち金：{money_check(author_id)}")
            await ctx.send("------------------------------")
        await ctx.send("終了")

bot.run(token)