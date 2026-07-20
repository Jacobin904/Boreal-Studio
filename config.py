import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Tokens & IDs
    TOKEN = os.getenv("BOT_TOKEN")
    GUILD_ID = 1527717135827206234
    OWNER_ID = 1321908994591297601
    DEVELOPER_ID = 1281784488854159421
    
    # Channels
    LOGS_CHANNEL = None  # Sera défini automatiquement
    TICKETS_CATEGORY = None
    COMMANDS_CHANNEL = None
    
    # Roles
    ROLE_FONDATEUR = None
    ROLE_DESIGNER = None
    ROLE_CLIENT = None
    ROLE_CLIENT_PREMIUM = None
    ROLE_MANAGER_TICKET = None
    
    # Embeds
    EMBED_COLOR = 0x00FFAA
    ERROR_COLOR = 0xFF0000
    SUCCESS_COLOR = 0x00FFAA
    WARNING_COLOR = 0xFFAA00
    
    # Prix
    PRICES = {
        "livery_simple": 20,
        "livery_custom": 40,
        "livery_detailed": 60,
        "livery_premium": 80,
        "livery_ultra": 100,
        "uniform": 35,
        "logo": 25
    }
    
    # Settings
    PREFIX = "!"
    XP_PER_MESSAGE = 10
    DAILY_REWARD = 100
    COOLDOWN_DAILY = 86400  # 24h en secondes
