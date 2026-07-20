import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import config
from database import Database

db = Database()

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title=" Boreal Studio - Menu Complet",
            description="Bot professionnel pour la gestion de commandes",
            color=config.Config.EMBED_COLOR,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1527717135827206234/b5b15b06ca5f6cb576895a8888687f2c.webp?size=1024")
        
        embed.add_field(
            name=" **Informations**",
            value="`!help` - Menu d'aide\n`!info` - Infos bot\n`!ping` - Latence\n`!serverinfo` - Stats serveur",
            inline=False
        )
        
        embed.add_field(
            name="💰 **Économie**",
            value="`!balance` - Solde\n`!daily` - Récompense\n`!work` - Travailler\n`!transfer @user <amount>` - Transférer",
            inline=False
        )
        
        embed.add_field(
            name="📈 **Niveaux**",
            value="`!rank` - Votre niveau\n`!leaderboard` - Top XP\n`!levels` - Infos niveaux",
            inline=False
        )
        
        embed.add_field(
            name=" **Tickets**",
            value="`!ticket` - Créer ticket\n`!close` - Fermer ticket\n`!add @user` - Ajouter\n`!transcript` - Historique",
            inline=False
        )
        
        embed.add_field(
            name="👥 **Équipe**",
            value=f"**Owner:** <@{config.Config.OWNER_ID}>\n**Dev:** <@{config.Config.DEVELOPER_ID}>",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="info")
    async def info(self, ctx):
        embed = discord.Embed(
            title="🌲 Boreal Studio Bot",
            description="Bot professionnel de gestion de commandes",
            color=config.Config.EMBED_COLOR
        )
        embed.add_field(name="Serveurs", value=len(bot.guilds), inline=True)
        embed.add_field(name="Utilisateurs", value=len(bot.users), inline=True)
        embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
        await ctx.send(embed=embed)
    
    @commands.command(name="rank")
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        data = db.get_level(member.id)
        
        if not data:
            await ctx.send("Aucune donnée trouvée")
            return
        
        embed = discord.Embed(
            title=f"📊 Rang de {member.display_name}",
            color=config.Config.EMBED_COLOR
        )
        embed.add_field(name="Niveau", value=data[2], inline=True)
        embed.add_field(name="XP", value=data[1], inline=True)
        embed.add_field(name="Messages", value=data[3], inline=True)
        await ctx.send(embed=embed)
    
    @commands.command(name="balance")
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        data = db.get_balance(member.id)
        
        if not data:
            await ctx.send("Aucun compte trouvé")
            return
        
        embed = discord.Embed(
            title=f"💰 Solde de {member.display_name}",
            color=config.Config.EMBED_COLOR
        )
        embed.add_field(name="Portefeuille", value=f"{data[1]} 🪙", inline=True)
        embed.add_field(name="Banque", value=f"{data[2]} 🪙", inline=True)
        embed.add_field(name="Total", value=f"{data[1] + data[2]} 🪙", inline=True)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
