import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
import pymongo
from pymongo import MongoClient
from keep_alive import keep_alive
from telegram.error import BadRequest

# MongoDB setup
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb+srv://wemedia360:DfQbsNu54pMHTkUy@deamxbotz1.lfquley.mongodb.net/?retryWrites=true&w=majority&appName=deamxbotz'))  # Enter MongoDB URl Here
db = client['autodelete']
settings_collection = db['settings']

# Loads settings from MongoDB (if any)
settings = settings_collection.find_one({"bot_settings": "general"})
if settings:
    ALLOWED_CHAT_IDS = set(settings.get("allowed_chat_ids", []))
    SUDO_USERS = set(settings.get("sudo_users", []))
    delete_timer = settings.get("delete_timer", 60)
    deletion_enabled = settings.get("deletion_enabled", True)
    delete_admins_enabled = settings.get("delete_admins_enabled", True)  # New setting for admins
else:
    ALLOWED_CHAT_IDS = set()
    SUDO_USERS = set()
    delete_timer = 60
    deletion_enabled = True
    delete_admins_enabled = True  # Default to deleting admins' messages

# Add Bot Token and Admin IDs
TOKEN = os.getenv('BOT_TOKEN', '8208550925:AAHas2c6vHZBFdW97gWFsq1OwlCv2_sbMLw')  # Bot Token
ADMIN_IDS = [1397269319]  # Add more admin IDs as needed

def is_admin_or_sudo(user_id):
    """Check if the user is an admin or a sudo user."""
    return user_id in ADMIN_IDS or user_id in SUDO_USERS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command, only accessible by admins or sudo users."""
    if not is_admin_or_sudo(update.effective_user.id):
        await update.message.reply_text("Unauthorized access.")
        return
    await update.message.reply_text("Welcome, Admin! Use /status to check bot status or /help for commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command, listing available bot commands."""
    await update.message.reply_text(
        "/start - Start bot\n"
        "/help - Show help\n"
        "/status - Show status\n"
        "/settings - Configure bot\n"
        "/add_chat <chat_id> - Allow a chat for deletion\n"
        "/remove_chat <chat_id> - Remove chat\n"
        "/toggle_deletion - Enable/Disable message deletion\n"
        "/toggle_admin_deletion - Enable/Disable admin message deletion"  # Added new command
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot status, only accessible by admins or sudo users."""
    if not is_admin_or_sudo(update.effective_user.id):
        await update.message.reply_text("Unauthorized access.")
        return
    status_text = (
        f"Bot is running.\n"
        f"Delete timer: {delete_timer} seconds\n"
        f"Deletion enabled: {deletion_enabled}\n"
        f"Admin deletion enabled: {delete_admins_enabled}\n"  # Display new setting
        f"Allowed chats: {', '.join(map(str, ALLOWED_CHAT_IDS)) or 'None'}\n"
        f"Sudo Users: {', '.join(map(str, SUDO_USERS)) or 'None'}"
    )
    await update.message.reply_text(status_text)

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Settings panel, only accessible by admins or sudo users."""
    if not is_admin_or_sudo(update.effective_user.id):
        await update.message.reply_text("Unauthorized access.")
        return
    keyboard = [
        [InlineKeyboardButton("🕐 Set Delete Timer", callback_data="set_timer")],
        [InlineKeyboardButton("✅ Add Chat ID", callback_data="add_chat"),
         InlineKeyboardButton("❌ Remove Chat ID", callback_data="remove_chat")],
        [InlineKeyboardButton("👑 Add Sudo User", callback_data="add_sudo"),
         InlineKeyboardButton("🚫 Remove Sudo User", callback_data="remove_sudo")],
        [InlineKeyboardButton("🔄 Toggle Deletion", callback_data="toggle_deletion")],
        [InlineKeyboardButton("🛠 Toggle Admin Msg Deletion", callback_data="toggle_admin_deletion")],  # New button
        [InlineKeyboardButton("📊 View Settings", callback_data="view_status")],
        [InlineKeyboardButton("🚪 Exit", callback_data="exit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text("⚙️ Bot Settings Panel:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("⚙️ Bot Settings Panel:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback query handler for buttons in the settings panel."""
    query = update.callback_query
    if not is_admin_or_sudo(update.effective_user.id):
        user_name = update.effective_user.username or (update.effective_user.first_name + ' ' + (update.effective_user.last_name or ''))
        
        await context.bot.send_message(
            chat_id=query.message.chat.id,  # Made By Downloader Zone
            text=f"@{user_name} You don't have permission to access this menu."
        )
        
        return
    
    try:
        await query.answer()
    except BadRequest as e:
        if "Query is too old" in str(e) or "query id is invalid" in str(e):
            await query.message.edit_text("❌ This menu is too old. Please use /settings to open a new menu.")
            return
        raise

    data = query.data

    if data == "toggle_admin_deletion":
        global delete_admins_enabled
        delete_admins_enabled = not delete_admins_enabled
        save_settings()
        status = "enabled" if delete_admins_enabled else "disabled"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
        await query.edit_message_text(f"🛠 Admin message deletion is now *{status}*.", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "set_timer":
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
        await query.edit_message_text("Send me the new delete timer in seconds:", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["awaiting_timer"] = True

    elif data == "add_chat":
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
        await query.edit_message_text("Send me the Chat ID to add:", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["awaiting_chat_add"] = True

    elif data == "remove_chat":
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
        await query.edit_message_text("Send me the Chat ID to remove:", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["awaiting_chat_remove"] = True

    elif data == "add_sudo":
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
        await query.edit_message_text("Send me the User ID to add as Sudo:", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["awaiting_sudo_add"] = True

    elif data == "remove_sudo":
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
        await query.edit_message_text("Send me the User ID to remove from Sudo list:", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["awaiting_sudo_remove"] = True

    elif data == "toggle_deletion":
        global deletion_enabled
        deletion_enabled = not deletion_enabled
        save_settings()
        status = "enabled" if deletion_enabled else "disabled"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
        await query.edit_message_text(f"🛠 Message deletion is now *{status}*.", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "view_status":
        status_text = (
            f"🤖 *Bot Status:*\n"
            f"Delete Timer: {delete_timer} seconds\n"
            f"Deletion Enabled: {deletion_enabled}\n"
            f"Admin Deletion Enabled: {delete_admins_enabled}\n"
            f"Allowed Chats: {', '.join(map(str, ALLOWED_CHAT_IDS)) or 'None'}\n"
            f"Sudo Users: {', '.join(map(str, SUDO_USERS)) or 'None'}"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
        await query.edit_message_text(status_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "back_to_settings":
        context.user_data.clear()
        await settings(update, context)

    elif data == "exit":
        await query.edit_message_text("❎ Settings panel closed.")
        context.user_data.clear()

async def add_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add chat ID to allowed chats, only accessible by admins or sudo users.""" 
    if not is_admin_or_sudo(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /add_chat <chat_id>")
        return
    try:
        chat_id = int(context.args[0])
        ALLOWED_CHAT_IDS.add(chat_id)
        save_settings()
        await update.message.reply_text(f"✅ Chat ID {chat_id} added.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid chat ID.")

async def remove_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove chat ID from allowed chats, only accessible by admins or sudo users."""
    if not is_admin_or_sudo(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /remove_chat <chat_id>")
        return
    try:
        chat_id = int(context.args[0])
        ALLOWED_CHAT_IDS.discard(chat_id)
        save_settings()
        await update.message.reply_text(f"✅ Chat ID {chat_id} removed.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid chat ID.")

async def add_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add user ID to sudo users, only accessible by admins or sudo users."""
    if not is_admin_or_sudo(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /add_sudo <user_id>")
        return
    try:
        user_id = int(context.args[0])
        SUDO_USERS.add(user_id)
        save_settings()
        await update.message.reply_text(f"✅ User ID {user_id} added as Sudo.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")

async def remove_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove user ID from sudo users, only accessible by admins or sudo users.""" 
    if not is_admin_or_sudo(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /remove_sudo <user_id>")
        return
    try:
        user_id = int(context.args[0])
        SUDO_USERS.discard(user_id)
        save_settings()
        await update.message.reply_text(f"✅ User ID {user_id} removed from Sudo.", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")

async def toggle_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle message deletion, only accessible by admins or sudo users.""" 
    if not is_admin_or_sudo(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    global deletion_enabled
    deletion_enabled = not deletion_enabled
    save_settings()
    await update.message.reply_text(f"✅ Deletion {'enabled' if deletion_enabled else 'disabled'}.")

def save_settings():
    """Save the settings to MongoDB."""
    settings_collection.update_one(
        {"bot_settings": "general"},
        {"$set": {
            "allowed_chat_ids": list(ALLOWED_CHAT_IDS),
            "sudo_users": list(SUDO_USERS),
            "delete_timer": delete_timer,
            "deletion_enabled": deletion_enabled,
            "delete_admins_enabled": delete_admins_enabled  # Save the new setting
        }},
        upsert=True
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if context.user_data.get("awaiting_timer"):
        try:
            global delete_timer
            delete_timer = int(update.message.text)
            if delete_timer < 1:
                raise ValueError("Timer must be positive")
            save_settings()
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
            await update.message.reply_text(f"✅ Timer updated to {delete_timer} seconds.", reply_markup=InlineKeyboardMarkup(keyboard))
        except ValueError:
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
            await update.message.reply_text("❌ Invalid input. Please enter a positive number.", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data.pop("awaiting_timer", None)

    elif context.user_data.get("awaiting_chat_add"):
        try:
            chat_id = int(update.message.text)
            ALLOWED_CHAT_IDS.add(chat_id)
            save_settings()
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
            await update.message.reply_text(f"✅ Chat ID {chat_id} added.", reply_markup=InlineKeyboardMarkup(keyboard))
        except ValueError:
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
            await update.message.reply_text("❌ Invalid input. Please enter a valid chat ID.", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data.pop("awaiting_chat_add", None)

    elif context.user_data.get("awaiting_chat_remove"):
        try:
            chat_id = int(update.message.text)
            ALLOWED_CHAT_IDS.discard(chat_id)
            save_settings()
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
            await update.message.reply_text(f"✅ Chat ID {chat_id} removed.", reply_markup=InlineKeyboardMarkup(keyboard))
        except ValueError:
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
            await update.message.reply_text("❌ Invalid input. Please enter a valid chat ID.", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data.pop("awaiting_chat_remove", None)

    elif context.user_data.get("awaiting_sudo_add"):
        try:
            user_id = int(update.message.text)
            SUDO_USERS.add(user_id)
            save_settings()
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
            await update.message.reply_text(f"✅ User ID {user_id} added.", reply_markup=InlineKeyboardMarkup(keyboard))
        except ValueError:
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
            await update.message.reply_text("❌ Invalid input. Please enter a valid user ID.", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data.pop("awaiting_sudo_add", None)

    elif context.user_data.get("awaiting_sudo_remove"):
        try:
            user_id = int(update.message.text)
            SUDO_USERS.discard(user_id)
            save_settings()
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
            await update.message.reply_text(f"✅ User ID {user_id} removed.", reply_markup=InlineKeyboardMarkup(keyboard))
        except ValueError:
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]]
            await update.message.reply_text("❌ Invalid input. Please enter a valid user ID.", reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data.pop("awaiting_sudo_remove", None)

    # Check deletion logic
    if deletion_enabled and chat_id in ALLOWED_CHAT_IDS:
        await asyncio.sleep(delete_timer)
        try:
            await update.message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors, particularly BadRequest for old callback queries.""" 
    if isinstance(context.error, BadRequest):
        if "Query is too old" in str(context.error) or "query id is invalid" in str(context.error):
            if update.callback_query:
                await update.callback_query.message.edit_text("❌ This menu is too old. Please use /settings to open a new menu.")
            elif update.message:
                await update.message.reply_text("❌ An error occurred. Please use /settings to open a new menu.")
            return
    print(f"Update {update} caused error {context.error}")

keep_alive()

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("add_chat", add_chat))
    app.add_handler(CommandHandler("remove_chat", remove_chat))
    app.add_handler(CommandHandler("add_sudo", add_sudo))
    app.add_handler(CommandHandler("remove_sudo", remove_sudo))
    app.add_handler(CommandHandler("toggle_deletion", toggle_deletion))
    app.add_handler(CommandHandler("settings", settings))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_error_handler(error_handler)

    print("Bot is running...")
    app.run_polling()


