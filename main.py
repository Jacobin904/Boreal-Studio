import discord
from discord.ext import commands, tasks
from discord.ui import Button, View, Modal, Select
import asyncio
import random
from datetime import datetime, timedelta
import config
from database import Database

# Initialisation
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(
    command_prefix=config.Config.PREFIX,
    intents=intents,
    case_insensitive=True,
    help_command=None
)

db = Database()

# Chargement des cogs
initial_extensions = [
    'cogs.tickets',
    'cogs.commands',
    'cogs.economy',
    'cogs.moderation',
    'cogs.stats',
    'cogs.utils'
]

@bot.event
async def on_ready():
    print(f'✅ {bot.user} connecté!')
    print(f'📊 {len(bot.guilds)} serveur(s)')
    print(f' {len(bot.users)} utilisateur(s)')
    
    # Changement de présence
    await update_presence()
    presence_rotation.start()
    
    # Sync des commandes slash
    try:
        synced = await bot.tree.sync()
        print(f"🔄 {len(synced)} commandes synchronisées")
    except Exception as e:
        print(f"❌ Erreur de sync: {e}")

async def update_presence():
    statuses = [
        "Boreal Studio | !help",
        " Liveries & Logos",
        f"{len(bot.users)} membres",
        "🚔 Qualité Premium"
    ]
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=random.choice(statuses)
        )
    )

@tasks.loop(hours=1)
async def presence_rotation():
    await update_presence()

# Système de niveaux
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.guild and message.guild.id == config.Config.GUILD_ID:
        # XP System
        level_data = db.add_xp(message.author.id, config.Config.XP_PER_MESSAGE)
        
        # Vérifier level up
        if level_data:
            current_level = level_data[2]
            new_level = int((2 * level_data[1] + 250) ** 0.5 / 10)
            
            if new_level > current_level:
                embed = discord.Embed(
                    title="🎉 NIVEAU SUPÉRIEUR!",
                    description=f"Félicitations {message.author.mention}!",
                    color=config.Config.EMBED_COLOR
                )
                embed.add_field(name="Niveau", value=f"**{current_level}** → **{new_level}**", inline=False)
                await message.channel.send(embed=embed)
    
    await bot.process_commands(message)

# Chargement des extensions
for extension in initial_extensions:
    try:
        bot.load_extension(extension)
        print(f"✅ {extension} chargé")
    except Exception as e:
        print(f"❌ Erreur {extension}: {e}")

if __name__ == "__main__":
    bot.run(config.Config.TOKEN)
