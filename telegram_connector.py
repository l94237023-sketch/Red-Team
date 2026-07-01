import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from command_queue import CommandQueue

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBAPP_URL = f"https://{os.getenv('REPL_SLUG')}.{os.getenv('REPL_OWNER')}.repl.co"
cmd_queue = CommandQueue()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👑 Open Ultimate Gold Suite", web_app={"url": WEBAPP_URL})],
        [InlineKeyboardButton("📚 Help", callback_data='help')]
    ]
    await update.message.reply_text(
        "👑 *ULTIMATE GOLD AGENTIC AI*\n\n"
        "🔥 *All commands work in this chat!*\n\n"
        "`strike <target> <level> <task>` - Attack\n"
        "  Levels: mobile, standard, gold\n"
        "  Tasks: full, modify, recon_only\n"
        "`plan <target> <level>` - Generate plan\n"
        "`add <capability>` - Evolve (adds only)\n"
        "`status` - Show AI stats\n"
        "`help` - This message\n\n"
        "Example: `strike 192.168.1.1 gold full`",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.startswith('/'):
        text = text[1:]
    if not text:
        return
    cmd_queue.add_command(update.effective_user.id, text)
    await update.message.reply_text(f"✅ Command sent to Gold AI:\n`{text}`", parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("👑 Ultimate Gold AI active. Type commands directly.")

def start_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
