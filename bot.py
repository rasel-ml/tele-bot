import os
import re
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = os.environ.get("BOT_TOKEN")


def clean_domain(url):
    try:
        domain = urlparse(url).netloc.lower()
        domain = domain.replace("www.", "")
        return domain.split(".")[0]
    except:
        return "unknown"


def format_message(text):
    if not text:
        return ""

    lines = text.split("\n")
    title = lines[0].strip()
    body = "\n".join(lines[1:]).strip()

    urls = re.findall(r'https?://\S+', text)

    grouped = {}
    for u in urls:
        d = clean_domain(u)
        grouped.setdefault(d, []).append(u)

    # remove URLs from body
    body_clean = re.sub(r'https?://\S+', '', body).strip()

    result = f"<b>{title}</b>\n\n"
    if body_clean:
        result += body_clean + "\n\n"

    for domain, links in grouped.items():
        result += f"<b>{domain.upper()}</b>\n"
        for i, link in enumerate(links, 1):
            result += f'|   <b><a href="{link}">{i}</a></b>   '
        result += "|\n\n"
    return result.strip()


async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post

    if not msg:
        return

    text = msg.text or msg.caption or ""
    if not text:
        return

    formatted = format_message(text)

    try:
        await context.bot.edit_message_text(
            chat_id=msg.chat_id,
            message_id=msg.message_id,
            text=formatted,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        print("Edit failed:", e)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_post))

print("Bot running...")
app.run_polling()