import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "TOKEN": os.getenv("BOT_TOKEN"),
    "GUILD_ID": 1527717135827206234,
    "OWNER_ID": 1321908994591297601,
    "DEVELOPER_ID": 1281784488854159421,
}
