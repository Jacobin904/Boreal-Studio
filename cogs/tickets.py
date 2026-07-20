import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, Select
from datetime import datetime
import config
from database import Database

db = Database()

class TicketCategorySelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🚔 Livery", description="Commander une livery", emoji="🚔"),
            discord.SelectOption(label="👕 Uniforme", description="Commander un uniforme", emoji="👕"),
            discord.SelectOption(label="🎖️ Logo", description="Commander un logo", emoji="️"),
            discord.SelectOption(label="📦 Pack Complet", description="Plusieurs services", emoji="📦"),
        ]
        super().__init__(
            placeholder="Choisissez le type de commande...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        await interaction.response.send_modal(TicketModal(category))

class TicketModal(Modal, title="Nouvelle Commande"):
    def __init__(self, category):
        super().__init__()
        self.category = category
        
        self.description = discord.ui.TextInput(
            label="Description de votre commande",
            style=discord.TextStyle.long,
            placeholder="Décrivez en détail ce que vous souhaitez...",
            required=True,
            max_length=1000
        )
        self.add_item(self.description)
        
        self.references = discord.ui.TextInput(
            label="Références (optionnel)",
            style=discord.TextStyle.long,
            placeholder="Liens d'images, exemples...",
            required=False,
            max_length=500
        )
        self.add_item(self.references)
    
    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # Créer catégorie si besoin
        category_name = "🎫・COMMANDES"
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name)
        
        # Créer channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_member(config.Config.OWNER_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_member(config.Config.DEVELOPER_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        
        channel = await guild.create_text_channel(
            f"commande-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )
        
        # Créer ticket en DB
        ticket_id = db.create_ticket(interaction.user.id, channel.id, self.category)
        
        # Créer order en DB
        price = self.get_price(self.category)
        order_id = db.create_order(ticket_id, interaction.user.id, self.category, self.description.value, price)
        
        # Message de bienvenue
        embed = discord.Embed(
            title="🎫 Commande Créée",
            description=f"Bienvenue {interaction.user.mention}!",
            color=config.Config.EMBED_COLOR,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Type", value=self.category, inline=True)
        embed.add_field(name="Prix estimé", value=f"{price} Robux", inline=True)
        embed.add_field(name="ID Ticket", value=f"#{ticket_id}", inline=True)
        embed.add_field(name="Description", value=self.description.value[:1024], inline=False)
        
        if self.references.value:
            embed.add_field(name="Références", value=self.references.value[:1024], inline=False)
        
        # Boutons
        start_button = Button(label="▶️ Commencer", style=discord.ButtonStyle.green, custom_id="start_order")
        progress_button = Button(label="📊 Progression", style=discord.ButtonStyle.blue, custom_id="show_progress")
        close_button = Button(label="❌ Fermer", style=discord.ButtonStyle.red, custom_id="close_ticket")
        
        class TicketView(View):
            def __init__(self):
                super().__init__(timeout=None)
            
            @discord.ui.button(label="✅ Commander (Payer)", style=discord.ButtonStyle.blurple, custom_id="pay_order")
            async def pay_button(self, interaction: discord.Interaction, button: Button):
                balance = db.get_balance(interaction.user.id)
                if balance and balance[1] >= price:
                    if db.remove_balance(interaction.user.id, price):
                        embed = discord.Embed(
                            title="✅ Paiement Confirmé",
                            description=f"{price} Robux débités de votre compte",
                            color=config.Config.SUCCESS_COLOR
                        )
                        db.update_order_progress(order_id, 1)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                    else:
                        await interaction.response.send_message("❌ Erreur de paiement", ephemeral=True)
                else:
                    await interaction.response.send_message(f"❌ Solde insuffisant. Prix: {price} Robux", ephemeral=True)
            
            @discord.ui.button(label="📊 Voir Progression", style=discord.ButtonStyle.gray, custom_id="check_progress")
            async def progress_btn(self, interaction: discord.Interaction, button: Button):
                # Récupérer progression
                await interaction.response.send_message("Progression: 0%", ephemeral=True)
        
        view = TicketView()
        view.add_item(close_button)
        
        await channel.send(embed=embed, view=view)
        await channel.send(f"👥 Staff concerné: <@{config.Config.OWNER_ID}> <@{config.Config.DEVELOPER_ID}>")
        
        await interaction.response.send_message(f"✅ Ticket créé: {channel.mention}", ephemeral=True)
    
    def get_price(self, category):
        prices = {
            "🚔 Livery": config.Config.PRICES["livery_custom"],
            "👕 Uniforme": config.Config.PRICES["uniform"],
            "🎖️ Logo": config.Config.PRICES["logo"],
            "📦 Pack Complet": 150
        }
        return prices.get(category, 50)

class TicketSystemView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketCategorySelect())

class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ticket")
    @commands.has_permissions(administrator=True)
    async def setup_ticket(self, ctx):
        embed = discord.Embed(
            title="🎫 Boreal Studio - Système de Commandes",
            description="""
            **Bienvenue sur notre système de commandes!**
            
            Cliquez sur le menu ci-dessous pour ouvrir un ticket et passer votre commande.
            
            **Nos Services:**
             Liveries personnalisées (20-100 Robux)
            👕 Uniformes (35 Robux)
            ️ Logos (25 Robux)
            📦 Packs complets
            """,
            color=config.Config.EMBED_COLOR,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1527717135827206234/b5b15b06ca5f6cb576895a8888687f2c.webp?size=1024")
        
        view = TicketSystemView()
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name="close")
    async def close_ticket(self, ctx):
        ticket = db.get_ticket(ctx.channel.id)
        if ticket:
            db.close_ticket(ticket[0], ctx.author.id)
            await ctx.channel.delete()
        else:
            await ctx.send(" Pas un channel de ticket", delete_after=5)

async def setup(bot):
    await bot.add_cog(TicketsCog(bot))
