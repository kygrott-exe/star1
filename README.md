# ⭐ Telegram Stars Payment Bot

Accept Telegram Stars payments via custom links, send buyers a custom message automatically.

---

## Setup

### 1. Get bot token
- Open [@BotFather](https://t.me/BotFather)
- `/newbot` → follow steps → copy the token

### 2. Enable Stars payments
- In BotFather: `/mybots` → your bot → **Payments**
- Enable **Telegram Stars**

### 3. Get your Telegram ID
- Message [@userinfobot](https://t.me/userinfobot) → it replies with your numeric ID

### 4. Configure
Edit `config.py`:
```python
BOT_TOKEN = "123456:ABC-xyz..."   # from BotFather
ADMIN_IDS = [123456789]           # your Telegram ID
```
Or use environment variables:
```bash
export BOT_TOKEN="your_token"
export ADMIN_IDS="123456789"
```

### 5. Install & run
```bash
pip install -r requirements.txt
python bot.py
```

---

## Admin Usage

| Command | Description |
|---|---|
| `/createlink 50 VIP Access` | Create a link costing 50 ⭐ |
| `/setmessage ABC123 Your invite: t.me/+xxx` | Set custom message for link ABC123 |
| `/links` | List all your links |
| `/deletelink ABC123` | Delete a link |
| `/stats` | View total earnings |

## User Flow

1. User sends `/pay ABC123` in the bot
2. Bot sends a Stars invoice
3. User pays
4. Bot sends them your custom message instantly
5. You (admin) get a notification with user info

---

## Multiple Admins
```python
ADMIN_IDS = [111111111, 222222222]
```
Each admin manages their own links independently.

---

## Notes
- Stars currency code is `XTR` in Telegram's API
- Minimum payment: 1 Star
- Payments are handled natively by Telegram — no third-party processor needed
- Data stored locally in `stars_bot.db` (SQLite)
