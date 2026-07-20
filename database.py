import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_name="data/boreal.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_database()
    
    def setup_database(self):
        # Système de niveaux
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS levels (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                messages INTEGER DEFAULT 0,
                last_message DATETIME
            )
        ''')
        
        # Système économique
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS economy (
                user_id INTEGER PRIMARY KEY,
                robux_balance INTEGER DEFAULT 0,
                bank INTEGER DEFAULT 0,
                last_daily DATETIME,
                total_earned INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0
            )
        ''')
        
        # Système de tickets
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                channel_id INTEGER,
                category TEXT,
                status TEXT DEFAULT 'open',
                priority TEXT DEFAULT 'normal',
                assigned_to INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                closed_at DATETIME,
                closed_by INTEGER
            )
        ''')
        
        # Système de commandes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER,
                user_id INTEGER,
                type TEXT,
                description TEXT,
                price INTEGER,
                status TEXT DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                payment_status TEXT DEFAULT 'unpaid',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                FOREIGN KEY (ticket_id) REFERENCES tickets(id)
            )
        ''')
        
        # Système de warnings
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                severity INTEGER DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Logs de transactions
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                type TEXT,
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Statistiques serveur
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_orders INTEGER,
                completed_orders INTEGER,
                revenue INTEGER,
                active_tickets INTEGER
            )
        ''')
        
        self.conn.commit()
    
    # Méthodes Levels
    def add_xp(self, user_id, amount):
        self.cursor.execute('SELECT * FROM levels WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        
        if result:
            new_xp = result[1] + amount
            new_messages = result[3] + 1
            new_level = int((2 * new_xp + 250) ** 0.5 / 10)
            
            self.cursor.execute('''
                UPDATE levels SET xp = ?, level = ?, messages = ?, last_message = ?
                WHERE user_id = ?
            ''', (new_xp, new_level, new_messages, datetime.now(), user_id))
        else:
            self.cursor.execute('''
                INSERT INTO levels (user_id, xp, level, messages, last_message)
                VALUES (?, ?, 1, 1, ?)
            ''', (user_id, amount, datetime.now()))
        
        self.conn.commit()
        return self.get_level(user_id)
    
    def get_level(self, user_id):
        self.cursor.execute('SELECT * FROM levels WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()
    
    # Méthodes Economy
    def add_balance(self, user_id, amount):
        self.cursor.execute('SELECT * FROM economy WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        
        if result:
            new_balance = result[1] + amount
            new_total = result[4] + amount
            self.cursor.execute('''
                UPDATE economy SET robux_balance = ?, total_earned = ?
                WHERE user_id = ?
            ''', (new_balance, new_total, user_id))
        else:
            self.cursor.execute('''
                INSERT INTO economy (user_id, robux_balance, total_earned, last_daily)
                VALUES (?, ?, ?, ?)
            ''', (user_id, amount, amount, datetime.now()))
        
        self.add_transaction(user_id, amount, "credit", "Ajout de balance")
        self.conn.commit()
    
    def remove_balance(self, user_id, amount):
        self.cursor.execute('SELECT * FROM economy WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        
        if result and result[1] >= amount:
            new_balance = result[1] - amount
            new_total_spent = result[5] + amount
            self.cursor.execute('''
                UPDATE economy SET robux_balance = ?, total_spent = ?
                WHERE user_id = ?
            ''', (new_balance, new_total_spent, user_id))
            self.add_transaction(user_id, amount, "debit", "Retrait de balance")
            self.conn.commit()
            return True
        return False
    
    def get_balance(self, user_id):
        self.cursor.execute('SELECT * FROM economy WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()
    
    # Méthodes Tickets
    def create_ticket(self, user_id, channel_id, category):
        self.cursor.execute('''
            INSERT INTO tickets (user_id, channel_id, category, status)
            VALUES (?, ?, ?, 'open')
        ''', (user_id, channel_id, category))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def close_ticket(self, ticket_id, closed_by):
        self.cursor.execute('''
            UPDATE tickets SET status = 'closed', closed_at = ?, closed_by = ?
            WHERE id = ?
        ''', (datetime.now(), closed_by, ticket_id))
        self.conn.commit()
    
    def get_ticket(self, channel_id):
        self.cursor.execute('SELECT * FROM tickets WHERE channel_id = ? AND status = "open"', (channel_id,))
        return self.cursor.fetchone()
    
    # Méthodes Commands
    def create_order(self, ticket_id, user_id, order_type, description, price):
        self.cursor.execute('''
            INSERT INTO orders (ticket_id, user_id, type, description, price)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticket_id, user_id, order_type, description, price))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_order_progress(self, order_id, progress):
        self.cursor.execute('''
            UPDATE orders SET progress = ? WHERE id = ?
        ''', (progress, order_id))
        if progress >= 100:
            self.cursor.execute('''
                UPDATE orders SET status = 'completed', completed_at = ?
                WHERE id = ?
            ''', (datetime.now(), order_id))
        self.conn.commit()
    
    # Méthodes Transactions
    def add_transaction(self, user_id, amount, type, description):
        self.cursor.execute('''
            INSERT INTO transactions (user_id, amount, type, description)
            VALUES (?, ?, ?, ?)
        ''', (user_id, amount, type, description))
        self.conn.commit()
    
    # Méthodes Warnings
    def add_warning(self, user_id, moderator_id, reason, severity=1):
        self.cursor.execute('''
            INSERT INTO warnings (user_id, moderator_id, reason, severity)
            VALUES (?, ?, ?, ?)
        ''', (user_id, moderator_id, reason, severity))
        self.conn.commit()
    
    def get_warnings(self, user_id):
        self.cursor.execute('SELECT * FROM warnings WHERE user_id = ?', (user_id,))
        return self.cursor.fetchall()
