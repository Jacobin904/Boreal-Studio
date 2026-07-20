import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
from datetime import datetime

# Configuration
CONFIG = {
    "GUILD_ID": 1527717135827206234,
    "OWNER_ID": 1321908994591297601,
    "DEVELOPER_ID": 1281784488854159421,
    "TOKEN": "YOUR_BOT_TOKEN_HERE"  # Remplace par ton token
}

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

# Événement de démarrage
@bot.event
async def on_ready():
    print(f'✅ {bot.user} est connecté!')
    print(f'📊 Serveurs: {len(bot.guilds)}')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Boreal Studio | !help"
        )
    )

# Commande help personnalisée
@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="🌲 Boreal Studio - Menu d'aide",
        description="Bienvenue sur le bot officiel de Boreal Studio!",
        color=0x00FFAA,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1454168707147370658/1528822407454916849/wpdx9z4.webp")
    embed.add_field(
        name=" Commandes disponibles",
        value="""
        `!help` - Affiche ce menu
        `!info` - Informations sur le bot
        `!team` - Présentation de l'équipe
        `!serverinfo` - Informations du serveur
        `!ping` - Vérifie la latence du bot
        """,
        inline=False
    )
    embed.add_field(
        name=" Équipe",
        value=f"""
        **Owner:** <@{CONFIG['OWNER_ID']}>
        **Developer:** <@{CONFIG['DEVELOPER_ID']}>
        """,
        inline=False
    )
    embed.set_footer(text="Boreal Studio © 2026")
    await ctx.send(embed=embed)

# Commande info
@bot.command(name="info")
async def info(ctx):
    embed = discord.Embed(
        title="🌲 À propos de Boreal Studio",
        description="""
        **Boreal Studio** est une entreprise spécialisée dans le développement 
        de solutions digitales innovantes.
        
        **Nos services:**
        • Développement de bots Discord
        • Création de sites web
        • Design graphique
        • Conseil en digital
        """,
        color=0x00C8FF,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1454168707147370658/1528822407454916849/wpdx9z4.webp")
    embed.add_field(name=" Liens", value="[Site Web](https://borealstudio.com) | [Discord](https://discord.gg/invite)", inline=False)
    await ctx.send(embed=embed)

# Commande team
@bot.command(name="team")
async def team(ctx):
    embed = discord.Embed(
        title="👥 Notre Équipe",
        color=0x00FFAA,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1454168707147370658/1528822407454916849/wpdx9z4.webp")
    
    # Owner
    embed.add_field(
        name="👑 Fondateur & Owner",
        value=f"""
        **Nom:** 𝙏𝘽 𝙧𝙞𝙢𝙚𝙨𝙩𝙖𝙧𝙤𝙭
        **Discord:** <@{CONFIG['OWNER_ID']}>
        **Username:** ytb_starox_14069
        """,
        inline=False
    )
    
    # Developer
    embed.add_field(
        name="💻 Développeur Principal",
        value=f"""
        **Nom:** Jacobin Babouain
        **Discord:** <@{CONFIG['DEVELOPER_ID']}>
        **Username:** jacobin904
        """,
        inline=False
    )
    
    await ctx.send(embed=embed)

# Commande ping
@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latence: **{latency}ms**",
        color=0x00FFAA
    )
    await ctx.send(embed=embed)

# Commande serverinfo
@bot.command(name="serverinfo")
@commands.has_permissions(administrator=True)
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title=f"📊 Informations - {guild.name}",
        color=0x00C8FF,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name=" ID", value=guild.id, inline=True)
    embed.add_field(name="👥 Membres", value=guild.member_count, inline=True)
    embed.add_field(name=" Créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name=" Owner", value=guild.owner.mention, inline=False)
    await ctx.send(embed=embed)

# Événement de bienvenue
@bot.event
async def on_member_join(member):
    if member.guild.id == CONFIG["GUILD_ID"]:
        embed = discord.Embed(
            title="🌲 Bienvenue sur Boreal Studio!",
            description=f"Bienvenue {member.mention} sur notre serveur!",
            color=0x00FFAA,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.add_field(
            name="📋 Pour commencer",
            value="Utilise la commande `!help` pour voir les commandes disponibles!",
            inline=False
        )
        
        channel = discord.utils.get(member.guild.text_channels, name="bienvenue")
        if channel:
            await channel.send(embed=embed)

# Système de tickets simple
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🎫 Ouvrir un ticket", style=discord.ButtonStyle.blurple)
    async def open_ticket(self, interaction: discord.Interaction, button: Button):
        category = discord.utils.get(interaction.guild.categories, name="・TICKETS")
        if not category:
            category = await interaction.guild.create_category("🎫・TICKETS")
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.get_member(CONFIG["OWNER_ID"]): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.get_member(CONFIG["DEVELOPER_ID"]): discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        
        channel = await interaction.guild.create_text_channel(
            f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )
        
        embed = discord.Embed(
            title="🎫 Ticket créé",
            description=f"Bonjour {interaction.user.mention}!\nUn membre de l'équipe va vous répondre rapidement.",
            color=0x00FFAA
        )
        
        close_button = Button(label="❌ Fermer le ticket", style=discord.ButtonStyle.red)
        
        async def close_ticket(interaction: discord.Interaction):
            await channel.delete()
        
        close_button.callback = close_ticket
        view = View()
        view.add_item(close_button)
        
        await channel.send(embed=embed, view=view)
        
        await interaction.response.send_message(f"Ticket créé: {channel.mention}", ephemeral=True)

@bot.command(name="ticket")
@commands.has_permissions(administrator=True)
async def ticket_setup(ctx):
    embed = discord.Embed(
        title="🎫 Système de tickets",
        description="Cliquez sur le bouton ci-dessous pour ouvrir un ticket et contacter l'équipe.",
        color=0x00FFAA
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1454168707147370658/1528822407454916849/wpdx9z4.webp")
    
    view = TicketView()
    await ctx.send(embed=embed, view=view)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Commande introuvable. Utilisez `!help` pour voir les commandes disponibles.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas les permissions nécessaires.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Arguments manquants.")

# Lancement du bot
if __name__ == "__main__":
    bot.run(CONFIG["TOKEN"])
