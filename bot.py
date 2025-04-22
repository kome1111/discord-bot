import discord
from discord.ext import commands
import os
import json
import asyncio
import random
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

data_file = "dice_data.json"
goc_data_file = "goc_data.json"
mob_data_file = "mob_data.json"
mf_data_file = "mf_data.json"
m7_data_file = "m7_data.json"
m7_rng_file = "m7_rng.json"
SETTINGS_FILE = "rng_settings.json"
rng_meter_file = "rng_meter.json"
m7_rng_settings = {}  # 最初に定義
rng_meter = {}
# ユーザーごとのrng設定を保存する辞書

def save_rng_meter():
    with open("rng_meter.json", "w", encoding="utf-8") as f:
        json.dump(rng_meter, f, ensure_ascii=False, indent=4)

def load_rng_meter():
    global rng_meter
    try:
        with open("rng_meter.json", "r", encoding="utf-8") as f:
            rng_meter = json.load(f)
    except FileNotFoundError:
        rng_meter = {}

def save_rng_settings():
    # m7_rng_settings を JSON 形式で保存
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(m7_rng_settings, f, ensure_ascii=False, indent=2)

# 保存データの読み込み
def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

user_data = load_data(data_file)
goc_data = load_data(goc_data_file)
mob_data_file = "mob_data.json"
mob_data = load_data(mob_data_file)
mf_data = load_data(mf_data_file)
m7_data = load_data(m7_data_file)

# 起動時に呼ばれる
def load_rng_settings():
    global m7_rng_settings
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            m7_rng_settings = json.load(f)
    else:
        m7_rng_settings = {}

load_rng_settings()
load_rng_meter()

@bot.event
async def on_ready():
    print(f"{bot.user} としてログインしました！")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

import discord
from discord.ext import commands
from discord.ui import View, Button
import random

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

class ExcludeGameView(View):
    def __init__(self, all_games):
        super().__init__(timeout=60)
        self.all_games = all_games
        self.excluded = set()
        self.confirmed = False

        # 各ゲームにボタンを作成
        for game in all_games:
            self.add_item(self.make_button(game))

    def make_button(self, game_name):
        return GameButton(label=game_name, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # すべてのユーザーが使えるようにしたい場合はTrueのままでOK
        return True


class GameButton(Button):
    def __init__(self, label, view: ExcludeGameView):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.game_name = label
        self.parent_view = view

    async def callback(self, interaction: discord.Interaction):
        if self.game_name in self.parent_view.excluded:
            self.parent_view.excluded.remove(self.game_name)
            self.style = discord.ButtonStyle.secondary
            self.label = self.game_name
            await interaction.response.send_message(f"✅ **{self.game_name}** を除外解除", ephemeral=True)
        else:
            self.parent_view.excluded.add(self.game_name)
            self.style = discord.ButtonStyle.danger
            self.label = f"🚫 {self.game_name}"
            await interaction.response.send_message(f"🚫 **{self.game_name}** を除外に追加", ephemeral=True)

        await interaction.message.edit(view=self.parent_view)


@bot.command()
async def r(ctx):
    all_games = [
        "Bed Wars", "SkyWars", "TNT Run", "Build Battle",
        "Murder Mystery", "Duels", "AA", "DE",
        "よくわからん洋館のやつ", "ダンジョン_m6",
        "ダンジョン_F7", "kuudra_any", "SMP", "寝る"
    ]

    view = ExcludeGameView(all_games)

    async def confirm_callback(interaction: discord.Interaction):
        filtered_games = [g for g in all_games if g not in view.excluded]
        if not filtered_games:
            await interaction.response.send_message("❌ 除外しすぎてゲームがなくなっちゃったよ！", ephemeral=True)
            return
        chosen = random.choice(filtered_games)
        embed = discord.Embed(
            title="🎲 今日やるのは…",
            description=f"**{chosen}** だ！！",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        view.stop()

    view.add_item(Button(label="🎯 決定する", style=discord.ButtonStyle.success, custom_id="confirm", row=4))
    view.children[-1].callback = confirm_callback

    await ctx.send("除外したいゲームをボタンで選んでください！\n（選択後、下の「🎯 決定する」を押してね）", view=view)

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
    ("Necron's Handle", 38, 0.00129, 700),
    ("Shadow Warp", 38, 0.00179, 200),
    ("Wither Shield", 38, 0.00179, 200),
    ("Implosion", 38, 0.00179, 200),
    ("Dark Claymore", 36, 0.000719, 20),
    ("Auto Recombobulator", 33, 0.00575, 0),
    ("Fifth Master Star", 32, 0.00215, 70),
    ("Wither Chestplate", 31, 0.00575, 0),
    ("One For All I", 29, 0.00575, 0),
    ("Master Skull - Tier 5", 25, 0.00172, 0),
    ("Recombobulator 3000", 25, 0.070236, 3.5),
    ("Wither Leggings", 25, 0.02303, 0),
    ("Wither Cloak Sword", 23, 0.03454, 0),
    ("Wither Helmet", 21, 0.03454, 0),
    ("Wither Blood", 21, 0.03454, 0),
    ("Thunderlord VII", 20, 0.00143, 0),
    ("Soul Eater I", 18, 0.05758, 0),
    ("Fuming Potato Book", 17, 0.02879, 0),
    ("Wither Boots", 17, 0.03454, 0),
    ("Wither Catalyst", 16, 0.02879, 0),
    ("Hot Potato Book", 16, 0.15783, 0),
    ("Precursor Gear", 14, 0.24675, 0),
    ("No Pain No Gain II", 12, 0.0964, 0),
    ("Combo II", 12, 0.22410, 0),
    ("Wisdom II", 10, 0.13305, 0),
    ("Ultimate Jerry III", 10, 0.15755, 0),
    ("Last Stand II", 10, 0.15755, 0),
    ("Feather Falling VII", 8, 0.355, 0),
    ("Infinite Quiver VII", 8, 0.24836, 0),
    ("Storm The Fish", 6, 0.056, 0),
    ("Maxor The Fish", 6, 0.056, 0),
    ("Goldor The Fish", 6, 0.056, 0),
    ("necron dye", 6, 0.0004, 8),
    ("Storm The Fish(left)", 6, 0.00036, 0),
    ("Maxor The Fish(left)", 6, 0.00036, 0),
    ("Goldor The Fish(left)", 6, 0.00036, 0),
]

@bot.command()
async def m7(ctx):
    user_id = str(ctx.author.id)
    
    if user_id not in m7_data:
        m7_data[user_id] = {"money": 0, "runs": 0, "obtained": []}
    if user_id not in rng_meter:
        rng_meter[user_id] = 0

    m7_data[user_id]["runs"] += 1

    # 失敗演出
    if random.random() < 0.01:
        await ctx.send(f"{ctx.author.mention} ゴミ野良が来たのでM7失敗！！💥")
        save_data(m7_data, m7_data_file)
        save_data(rng_meter, rng_meter_file)
        return

    base_rewards = ["Undead Essence (125)", "Wither Essence (100)"]
    qol_sum = 10
    drop = None

    rng_target = m7_rng_settings.get(user_id)
    rng_hit = False

    # RNGメーター天井処理
    if rng_target:
        cap = rng_caps.get(rng_target)
        if cap and rng_meter[user_id] >= cap:
            for name, qol, _, profit in m7_rewards:
                if name == rng_target:
                    drop = (name, qol, profit)
                    qol_sum += qol
                    rng_hit = True
                    rng_meter[user_id] = 0  # リセット
                    break

    if not drop:
        for name, qol, chance, profit in sorted(m7_rewards, key=lambda x: (-x[3], x[1])):
            if random.random() < chance and qol_sum + qol <= 441:
                drop = (name, qol, profit)
                qol_sum += qol
                break

    # RNGメーター進行（天井でヒットしてない場合のみ）
    if rng_target and not rng_hit:
        if not drop or drop[0] != rng_target:
            rng_meter[user_id] += 1

    embed = discord.Embed(title="📦 M7チェスト報酬", description=f"{ctx.author.mention} の報酬結果", color=discord.Color.gold())
    embed.add_field(name="基本報酬", value="\n".join(base_rewards), inline=False)

    if drop:
        embed.add_field(name="レア報酬", value=f"💎 {drop[0]}", inline=False)
        embed.add_field(name="利益", value=f"{drop[2]}m", inline=False)
        m7_data[user_id]["money"] += drop[2]
        if drop[0] not in m7_data[user_id]["obtained"]:
            m7_data[user_id]["obtained"].append(drop[0])
    else:
        embed.add_field(name="レア報酬", value="📦 レア報酬はありませんでした", inline=False)

    embed.set_footer(text=f"合計QoL: {qol_sum}/441 ・ 実行回数: {m7_data[user_id]['runs']}回")

    await ctx.send(embed=embed)
    save_data(m7_data, m7_data_file)
    save_data(rng_meter, rng_meter_file)

save_rng_meter()

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

from discord.ui import Button, View

import discord
from discord.ext import commands

# ユーザーごとのRNG設定データ
m7_rng_settings = {}

class RNGSettingView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

        # 選択肢
        options = ["Handle", "Implosion", "Wither Shield", "Shadow Warp"]
        for option in options:
            self.add_item(RNGButton(label=option, user_id=user_id))

        self.add_item(ClearButton(user_id=user_id))

class RNGButton(discord.ui.Button):
    def __init__(self, label, user_id):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=f"rng_{label.lower().replace(' ', '_')}")
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("これはあなた専用の設定メニューです。", ephemeral=True)

        m7_rng_settings[str(self.user_id)] = self.label
        save_rng_settings()
        await interaction.response.send_message(f"🎯 RNGメーターを `{self.label}` に設定しました！", ephemeral=True)

class ClearButton(discord.ui.Button):
    def __init__(self, user_id):
        super().__init__(label="設定解除", style=discord.ButtonStyle.danger, custom_id="rng_clear")
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("これはあなた専用の設定メニューです。", ephemeral=True)

        if str(self.user_id) in m7_rng_settings:
            del m7_rng_settings[str(self.user_id)]

            save_rng_settings()
            await interaction.response.send_message("❌ RNGメーター設定を解除しました。", ephemeral=True)
        else:
            await interaction.response.send_message("⚠ 設定されているRNGメーターがありません。", ephemeral=True)

# コマンド
@bot.command()
async def rng_set(ctx):
    """RNGメーターの設定メニュー"""
    view = RNGSettingView(ctx.author.id)
    await ctx.send("🎯 RNGメーターの設定を選んでください！", view=view)

rng_caps = {
    "Handle": 600,
    "Implosion": 500,
    "Wither Shield": 500,
    "Shadow Warp": 500
}

@bot.command()
async def rng_status(ctx):
    user_id = str(ctx.author.id)

    if user_id not in m7_rng_settings:
        await ctx.send(f"{ctx.author.mention} 現在、RNGメーターは設定されていません。`!rng_set` コマンドで設定してください。")
        return

    target = m7_rng_settings[user_id]
    cap = rng_caps.get(target, "?")
    current = rng_meter.get(user_id, 0)

    embed = discord.Embed(title="🎯 RNGメーター状況", color=discord.Color.blue())
    embed.add_field(name="対象アイテム", value=target, inline=False)
    embed.add_field(name="進行状況", value=f"{current} / {cap}", inline=False)

    await ctx.send(embed=embed)

keep_alive()
bot.run(TOKEN)