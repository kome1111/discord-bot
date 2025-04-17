import discord
from discord.ext import commands
import random
import os
import json
import asyncio


intents = discord.Intents.default()
intents.message_content = True  # メッセージの内容を読み取るには必要

bot = commands.Bot(command_prefix="!", intents=intents)

data_file = "dice_data.json"
goc_data_file = "goc_data.json"
mob_data_file = "mob_data.json"
mf_data_file = "mf_data.json"
m7_data_file = "m7_data.json"

# 保存データの読み込み
def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

# 保存データの保存
def save_data(data, file):
    with open(file, "w") as f:
        json.dump(data, f)

user_data = load_data(data_file)
goc_data = load_data(goc_data_file)
mob_data_file = "mob_data.json"
mob_data = load_data(mob_data_file)
mf_data = load_data(mf_data_file)
m7_data = load_data(m7_data_file)
@bot.event
async def on_ready():
    print(f"{bot.user} としてログインしました！")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def r(ctx, *, exclude: str = ""):
    all_games = [
        "Bed Wars", "SkyWars", "TNT Run", "Build Battle",
        "Murder Mystery", "Duels", "AA", "DE",
        "よくわからん洋館のやつ", "ダンジョン_m6",
        "ダンジョン_F7", "kuudra_any", "SMP", "寝る"
    ]
    exclude_list = [game.strip().lower() for game in exclude.split(",") if game.strip()]
    filtered_games = [game for game in all_games if game.lower() not in exclude_list]
    if not filtered_games:
        await ctx.send("❌ 除外しすぎてゲームがなくなっちゃったよ！")
        return
    chosen = random.choice(filtered_games)
    await ctx.send(f"🎲 除外ゲームをのぞいてランダム選択中...\n今日やるのは… **{chosen}** だ！！")

@bot.command()
async def dice(ctx):
    user_id = str(ctx.author.id)
    if user_id not in user_data:
        user_data[user_id] = {"tries": 0, "total_cost": 0}

    user_data[user_id]["tries"] += 1
    user_data[user_id]["total_cost"] += 6.6

    roll = random.choices([1, 2, 3, 4, 5, 6, 7], weights=[15, 15, 15, 15, 15, 1, 1], k=1)[0]

    if roll == 6:
        await ctx.send(f"🎉 {ctx.author.mention} 6が出た！おめでとう！\nここまでに使った金額: {user_data[user_id]['total_cost']:.1f}m")
        user_data[user_id]["tries"] = 0
        user_data[user_id]["total_cost"] = 0
    elif roll == 7:
        await ctx.send(f"💎 {ctx.author.mention} あーあ７出ちゃったよ")
    else:
        await ctx.send(f"🎲 {ctx.author.mention} の出目は {roll} でした！")

    save_data(user_data, data_file)

@bot.command()
async def dice_top(ctx):
    if not user_data:
        await ctx.send("データがまだありません！")
        return

    top_users = sorted(user_data.items(), key=lambda x: x[1]['total_cost'], reverse=True)[:5]
    msg = "💰 Top Diceギャンブラー 💰\n"
    for uid, stats in top_users:
        user = await bot.fetch_user(int(uid))
        msg += f"{user.name}: {stats['total_cost']:.1f}m 使用中 ({stats['tries']} 回試行中)\n"

    await ctx.send(msg)

@bot.command()
async def goc(ctx):
    attributes = [
        "Arachno Resistance", "Blazing Resistance", "Experience", "Speed",
        "Undead Resistance", "Breeze", "Lifeline", "Life Regeneration",
        "Mana Pool", "Dominance", "Ender Resistance", "Mana Regeneration",
        "Veteran", "Vitality", "Fortitude", "Magic Find"
    ]

    user_id = str(ctx.author.id)
    if user_id not in goc_data:
        goc_data[user_id] = {"net": 0.0, "count": 0}

    attr1, attr2 = random.sample(attributes, 2)
    goc_data[user_id]["net"] -= 5.0
    goc_data[user_id]["count"] += 1

    msg = f"🎁 {ctx.author.mention} の属性ガチャ結果：\n➡️ {attr1} + {attr2}"

    special = [("Mana Pool", "Dominance"), ("Dominance", "Speed")]
    if (attr1, attr2) in special or (attr2, attr1) in special:
        goc_data[user_id]["net"] += 100.0
        msg += f"\n💥 GOD ROLL！ +100mボーナス！"

    save_data(goc_data, goc_data_file)
    await ctx.send(msg)

@bot.command()
async def goc_total(ctx):
    user_id = str(ctx.author.id)
    if user_id not in goc_data:
        await ctx.send("データがまだありません！")
        return
    net = goc_data[user_id]["net"]
    count = goc_data[user_id]["count"]
    await ctx.send(f"📊 {ctx.author.mention} のattribute結果：\n合計試行回数: {count} 回\n収支: {net:+.1f}m")

@bot.command()
async def drag(ctx, eyes: int):
    dragon_types = {
        "Protector": 16,
        "Old": 16,
        "Unstable": 16,
        "Young": 16,
        "Strong": 16,
        "Wise": 16,
        "Superior": 4
    }

    unique_drops = []
    fragments = True
    ender_pearl = True

    dragon = random.choices(
        population=list(dragon_types.keys()),
        weights=list(dragon_types.values()),
        k=1
    )[0]

    drop_pool = []

    if dragon == "Superior":
        if random.random() < 0.3:
            drop_pool.append("Dragon Horn")

    if random.random() < eyes * 0.02:
        drop_pool.append("Dragon Claw")

    if random.random() < eyes * 0.0005:
        drop_pool.append("Ender Dragon Pet（EPIC）")

    if random.random() < eyes * 0.0001:
        drop_pool.append("Ender Dragon Pet（LEGENDARY）")

    if random.random() < 0.3:
        drop_pool.append(f"{dragon} Dragon Armor")

    unique_drop = random.choice(drop_pool) if drop_pool else None

    embed = discord.Embed(
        title="ドラゴン討伐完了！",
        description=f"{ctx.author.mention} がドラゴンを召喚！",
        color=discord.Color.gold()
    )

    # 🔥 GIFをタイトル横に表示
    embed.set_thumbnail(url="https://files.oaiusercontent.com/file-SDT5X6z4i3J9CWsN6ozsYn?se=2025-04-17T03%3A11%3A58Z&sp=r&sv=2024-08-04&sr=b&rscc=max-age%3D299%2C%20immutable%2C%20private&rscd=attachment%3B%20filename%3Dender-dragon-end-dragon.gif&sig=IXE585oP9ba4u3nRB%2BOiXgVB59N2U6Jdyrq1hWxsQHk%3D")

    embed.add_field(name="ドラゴンの種類", value=dragon, inline=False)

    drops = ""
    if ender_pearl:
        drops += "• Ender Pearl\n"
    if fragments:
        drops += f"• {dragon} Fragment ×数個\n"
    if unique_drop:
        drops += f"💎 {unique_drop}\n"

    embed.add_field(name="ドロップ内容", value=drops or "なし", inline=False)
    embed.set_footer(text=f"使用したSummoning Eye: {eyes}個")

    await ctx.send(embed=embed)

@bot.command()
async def mob(ctx):
    user_id = str(ctx.author.id)
    if user_id not in mob_data:
        mob_data[user_id] = {"since": 0, "inquisitors": 0, "rare_drops": 0}
    if user_id not in mf_data:
        mf_data[user_id] = 1.0

    mob_data[user_id]["since"] += 1
    mf = mf_data[user_id]

    mobs = [
        ("Minos Hunter", 12.35),
        ("Siamese Lynx", 18.52),
        ("Minotaur", 24.69),
        ("Gaia Construct", 24.69),
        ("Minos Champion", 18.52),
        ("Minos Inquisitor", 1.23),
        ("choco_desu", 0.1),
    ]

    names, weights = zip(*mobs)
    chosen = random.choices(names, weights=weights, k=1)[0]

    embed = discord.Embed(
        title="神話イベント：Mob出現！",
        description=f"{ctx.author.mention} は **{chosen}** に遭遇した！",
        color=discord.Color.green()
    )

    drop_msg = ""
    got_rare = False

    if chosen == "Minotaur" and random.random() < 0.0008 * mf:
        drop_msg += "🎁 Daedalus Stick ドロップ！\n"
        got_rare = True

    elif chosen == "Minos Champion" and random.random() < 0.0002 * mf:
        drop_msg += "🎁 Minos Relic ドロップ！\n"
        got_rare = True

    elif chosen == "Minos Inquisitor":
        drop_msg += "👁️ Minos Inquisitorが現れた...！\n"
        mob_data[user_id]["inquisitors"] += 1

        drops = [
            ("Chimera", 0.01),
            ("Shelmet", 0.01),
            ("Tiger", 0.01),
            ("花", 0.01)
        ]

        await ctx.send(embed=embed)
        await asyncio.sleep(1.5)

        for drop, chance in drops:
            if random.random() < chance * mf:
                drop_msg += f"🎁 {drop} ドロップ！\n"
                got_rare = True

        mob_data[user_id]["since"] = 0

        if got_rare:
            mob_data[user_id]["rare_drops"] += 1

        result_embed = discord.Embed(
            title="ドロップ結果",
            description=drop_msg.strip(),
            color=discord.Color.gold() if got_rare else discord.Color.greyple()
        )
        await ctx.send(embed=result_embed)
        save_data(mob_data, mob_data_file)
        save_data(mf_data, mf_data_file)
        return

    elif chosen == "choco_desu":
        drop_msg += "🎉 choco_desu降臨！最悪だ！\n"

    if got_rare:
        mob_data[user_id]["rare_drops"] += 1

    if drop_msg:
        embed.add_field(name="ドロップ結果", value=drop_msg.strip(), inline=False)
    else:
        embed.add_field(name="ドロップ結果", value="❌ 特に何もドロップしなかった...", inline=False)

    await ctx.send(embed=embed)

    save_data(mob_data, mob_data_file)
    save_data(mf_data, mf_data_file)

@bot.command()
async def since(ctx):
    user_id = str(ctx.author.id)
    if user_id in mob_data:
        await ctx.send(f"🔍 {ctx.author.mention} は {mob_data[user_id]['since']} 回連続でInquisitorを引いていません。")
    else:
        await ctx.send("データがありません！")


@bot.command()
async def setmf(ctx, multiplier: float):
    user_id = str(ctx.author.id)
    if multiplier <= 0:
        await ctx.send("倍率は0より大きい数にしてね！")
        return
    mf_data[user_id] = multiplier
    save_data(mf_data, mf_data_file)
    await ctx.send(f"✨ {ctx.author.mention} のレアドロップ倍率を {multiplier} 倍に設定したよ！")

@bot.command()
async def mob_droprank(ctx):
    if not mob_data:
        await ctx.send("データがまだありません！")
        return

    sorted_users = sorted(
        mob_data.items(),
        key=lambda x: x[1].get("rare_drops", 0),
        reverse=True
    )

    embed = discord.Embed(
        title="💎 レアドロップランキング",
        color=discord.Color.gold()
    )

    for i, (uid, stats) in enumerate(sorted_users[:5], start=1):
        user = await bot.fetch_user(int(uid))
        count = stats.get("rare_drops", 0)
        embed.add_field(
            name=f"{i}. {user.name}",
            value=f"{count} 個のレアドロップ",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
async def mob_inqrank(ctx):
    if not mob_data:
        await ctx.send("データがまだありません！")
        return

    sorted_users = sorted(
        mob_data.items(),
        key=lambda x: x[1].get("inquisitors", 0),
        reverse=True
    )

    embed = discord.Embed(
        title="👁️ Inquisitor 遭遇ランキング",
        color=discord.Color.purple()
    )

    for i, (uid, stats) in enumerate(sorted_users[:5], start=1):
        user = await bot.fetch_user(int(uid))
        count = stats.get("inquisitors", 0)
        embed.add_field(
            name=f"{i}. {user.name}",
            value=f"{count} 回出現",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name="helps")
async def helps(ctx):
    embed = discord.Embed(
        title="📖 Botコマンド一覧",
        description="現在使えるコマンドはこちら！",
        color=discord.Color.blurple()
    )

    embed.add_field(name="🎮 ゲーム系", value="ゲーム関連コマンド", inline=False)
    embed.add_field(name="!ping", value="Botが生きてるか確認するよ", inline=False)
    embed.add_field(name="!r [除外ゲーム1, 除外ゲーム2,...]", value="遊ぶゲームをランダムで選ぶ（除外もできる）", inline=False)

    embed.add_field(name="🎲 ギャンブル系", value="diceガチャなど", inline=False)
    embed.add_field(name="!dice", value="ダイスを振って6を狙え！（コスト計算付き）", inline=False)
    embed.add_field(name="!dice_top", value="一番お金を溶かしてる人を表示", inline=False)

    embed.add_field(name="🌀 Attributeガチャ", value="GoC属性厳選っぽいやつ", inline=False)
    embed.add_field(name="!goc", value="属性ガチャを1回回す（コスト -5m）", inline=False)
    embed.add_field(name="!goc_total", value="合計試行回数と収支を確認", inline=False)

    embed.add_field(name="🐲 ドラゴン再現", value="Summoning Eye数でレアドロップ確率UP", inline=False)
    embed.add_field(name="!drag [eye数]", value="ドラゴンを召喚してドロップを確認", inline=False)

    embed.add_field(name="🗿 神話イベント", value="Mythological Ritualの再現", inline=False)
    embed.add_field(name="!mob", value="Mobを1体召喚、Inquisitorやレアドロップあり", inline=False)
    embed.add_field(name="!since", value="最後にInquisitorを引いてからの回数を表示", inline=False)
    embed.add_field(name="!setmf [倍率]", value="レアドロップ倍率を設定（デフォルトは1.0）", inline=False)
    embed.add_field(name="!mob_droprank", value="レアドロップ数のランキング表示", inline=False)
    embed.add_field(name="!mob_inqrank", value="Inquisitor遭遇回数のランキング表示", inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def sibakuzo(ctx):
    responses = [
        "ごめんなさい…許して…🙏",
        "すいませんでしたああああ！！🙇‍♂️",
        "ヒィィィ…ごめんなさいぃ…😭",
        "怒らないでぇぇぇぇ！😢"
    ]
    await ctx.send(f"{ctx.author.mention} {random.choice(responses)}")

# 報酬リスト
def load_data(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

m7_data = load_data(m7_data_file)

m7_rewards = [
    ("Necron's Handle", 380, 0.00129, 700),
    ("Shadow Warp", 380, 0.00179, 200),
    ("Wither Shield", 380, 0.00179, 200),
    ("Implosion", 380, 0.00179, 200),
    ("Dark Claymore", 360, 0.000719, 20),
    ("Auto Recombobulator", 330, 0.00575, 0),
    ("Fifth Master Star", 320, 0.00215, 70),
    ("Wither Chestplate", 310, 0.00575, 0),
    ("One For All I", 290, 0.00575, 0),
    ("Master Skull - Tier 5", 250, 0.00172, 0),
    ("Recombobulator 3000", 250, 0.070236, 3.5),
    ("Wither Leggings", 250, 0.02303, 0),
    ("Wither Cloak Sword", 230, 0.03454, 0),
    ("Wither Helmet", 210, 0.03454, 0),
    ("Wither Blood", 210, 0.03454, 0),
    ("Thunderlord VII", 200, 0.00143, 0),
    ("Soul Eater I", 180, 0.05758, 0),
    ("Fuming Potato Book", 175, 0.02879, 0),
    ("Wither Boots", 170, 0.03454, 0),
    ("Wither Catalyst", 160, 0.02879, 0),
    ("Hot Potato Book", 160, 0.15783, 0),
    ("Precursor Gear", 140, 0.24675, 0),
    ("No Pain No Gain II", 120, 0.0964, 0),
    ("Combo II", 120, 0.22410, 0),
    ("Wisdom II", 100, 0.13305, 0),
    ("Ultimate Jerry III", 100, 0.15755, 0),
    ("Last Stand II", 100, 0.15755, 0),
    ("Feather Falling VII", 80, 0.355, 0),
    ("Infinite Quiver VII", 80, 0.24836, 0),
    ("Storm The Fish", 61, 0.056, 0),
    ("Maxor The Fish", 61, 0.056, 0),
    ("Goldor The Fish", 61, 0.056, 0),
    ("necron dye", 61, 0.0004, 8),
    ("Storm The Fish(left)", 61, 0.00036, 0),
    ("Maxor The Fish(left)", 61, 0.00036, 0),
    ("Goldor The Fish(left)", 61, 0.00036, 0),
]

@bot.command()
async def m7(ctx):
    user_id = str(ctx.author.id)

    # 初期化（古いデータ形式でも対応）
    if user_id not in m7_data:
        m7_data[user_id] = {
            "money": 0,
            "runs": 0,
            "obtained": []
        }
    else:
        m7_data[user_id].setdefault("money", 0)
        m7_data[user_id].setdefault("runs", 0)
        m7_data[user_id].setdefault("obtained", [])

    m7_data[user_id]["runs"] += 1

    # 1%の失敗演出
    if random.random() < 0.01:
        await ctx.send(f"{ctx.author.mention} ゴミ野良が来たのでM7失敗！！💥")
        save_data(m7_data, m7_data_file)
        return

    base_rewards = ["Undead Essence (125)", "Wither Essence (100)"]
    qol_sum = 100 + 100
    drop = None

    # ドロップ選出（QoL上限441以内で最大利益優先）
    for name, qol, chance, profit in sorted(m7_rewards, key=lambda x: (-x[3], x[1])):
        if random.random() < chance and qol_sum + qol <= 441:
            drop = (name, qol, profit)
            qol_sum += qol
            break

    # Embed構築
    embed = discord.Embed(
        title="📦 M7チェスト報酬",
        description=f"{ctx.author.mention} の報酬結果",
        color=discord.Color.gold()
    )
    embed.add_field(name="基本報酬", value="\n".join(base_rewards), inline=False)

    if drop:
        embed.add_field(name="レア報酬", value=f"💎 {drop[0]}", inline=False)
        embed.add_field(name="利益", value=f"{drop[2]}m", inline=False)
        m7_data[user_id]["money"] += drop[2]

        # 取得記録に追加（重複なし）
        if drop[0] not in m7_data[user_id]["obtained"]:
            m7_data[user_id]["obtained"].append(drop[0])
            save_data(m7_data, m7_data_file)
    else:
        embed.add_field(name="レア報酬", value="📦 レア報酬はありませんでした", inline=False)

    embed.set_footer(text=f"合計QoL: {qol_sum}/441 ・ 実行回数: {m7_data[user_id]['runs']}回")

    await ctx.send(embed=embed)
    save_data(m7_data, m7_data_file)




@bot.command()
async def m7_rank(ctx):
    ranking = sorted(m7_data.items(), key=lambda x: x[1].get("money", 0), reverse=True)

    embed = discord.Embed(
        title="🏆 M7利益ランキング (Top 10)",
        color=discord.Color.gold()
    )

    for i, (user_id, data) in enumerate(ranking[:10], 1):
        user = await bot.fetch_user(int(user_id))
        money = data.get("money", 0)
        embed.add_field(name=f"{i}. {user.name}", value=f"{money:.1f}m", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def m7_comp(ctx):
    user_id = str(ctx.author.id)
    count = m7_data.get(user_id, {}).get("count", 0)

    embed = discord.Embed(
        title="📊 M7周回記録",
        description=f"{ctx.author.mention} の今までのM7クリア回数は…",
        color=discord.Color.teal()
    )
    embed.add_field(name="🌀 総回数", value=f"{count} 回", inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def m7_checkdrop(ctx, *, item_name: str):
    item_name = item_name.strip().lower()

    found = None
    for name, qol, chance, profit in m7_rewards:
        if item_name == name.lower():
            found = (name, qol, chance, profit)
            break

    if not found:
        await ctx.send(f"❌ '{item_name}' はM7報酬リストに見つかりませんでした。")
        return

    name, qol, chance, profit = found
    embed = discord.Embed(
        title="🔍 M7 ドロップ情報",
        description=f"『{name}』の情報はこちら！",
        color=discord.Color.blue()
    )
    embed.add_field(name="🎯 ドロップ確率", value=f"{chance * 100:.5f}%", inline=False)
    embed.add_field(name="📦 QoL値", value=str(qol), inline=True)
    embed.add_field(name="💰 利益", value=f"{profit}m", inline=True)

    await ctx.send(embed=embed)

@bot.command()
async def m7_hype(ctx):
    user_id = str(ctx.author.id)
    if user_id not in m7_data:
        await ctx.send(f"{ctx.author.mention} のデータがありません！まずは `!m7` を実行してみてね！")
        return

    obtained = m7_data[user_id].get("obtained", [])

    required_items = ["Necron's Handle", "Wither Shield", "Shadow Warp", "Implosion"]
    missing_items = [item for item in required_items if item not in obtained]

    embed = discord.Embed(
        title="⚔️ Hyperion素材チェック",
        color=discord.Color.dark_purple()
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else discord.Embed.Empty)

    if not missing_items:
        embed.description = f"🎉 {ctx.author.mention} はすでに **Hyperion** を作成できます！おめでとう！\n（必要素材：Handle, Warp, Shield, Implosion）"
    else:
        embed.description = f"🧱 {ctx.author.mention} はまだHyperionを作ることができません。\n"
        embed.add_field(name="❌ 足りない素材", value="\n".join(missing_items), inline=False)
        embed.set_footer(text="ドロップは !m7 で集めよう！")

    await ctx.send(embed=embed)


bot.run("")



