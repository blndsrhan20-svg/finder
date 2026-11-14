import logging
import os
import re
from urllib.parse import urlparse

import phonenumbers
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("nando_finder")
TOKEN = os.environ.get("BOT_TOKEN", "").strip()

HELP = (
    "أوامر NANDO FINDER:\n"
    "/id - عرض رقم حسابك ومعرّف المحادثة\n"
    "/phone +964XXXXXXXXXX - فحص صيغة رقم هاتف فقط\n"
    "/url example.com - فحص أولي للرابط\n"
    "/lookup username - فتح رابط حساب تيليغرام العام\n"
    "/help - عرض المساعدة\n\n"
    "لا يكشف البوت هوية أصحاب الأرقام أو البيانات الخاصة."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("أهلاً بك في NANDO FINDER.\nأدوات تحقق بسيطة وآمنة للمعلومات العامة.\n\n" + HELP)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(HELP)

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    await update.effective_message.reply_text(f"معرّف حسابك: {user.id}\nمعرّف المحادثة: {chat.id}")

async def phone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.effective_message.reply_text("اكتب الرقم مع رمز الدولة. مثال: /phone +9647XXXXXXXXX")
        return
    raw = "".join(context.args).strip()
    try:
        number = phonenumbers.parse(raw, None)
        possible = phonenumbers.is_possible_number(number)
        valid = phonenumbers.is_valid_number(number)
        region = phonenumbers.region_code_for_number(number) or "غير معروف"
        formatted = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        status = "صالح حسب خطة الترقيم" if valid else ("محتمل من ناحية الطول" if possible else "غير صالح/غير محتمل")
        await update.effective_message.reply_text(f"الرقم: {formatted}\nالدولة/المنطقة: {region}\nالنتيجة: {status}\n\nهذا الفحص لا يحدد مالك الرقم ولا يؤكد أنه مستخدم.")
    except phonenumbers.NumberParseException:
        await update.effective_message.reply_text("تعذّر تحليل الرقم. استخدم رمز الدولة مثل +964.")

async def url_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.effective_message.reply_text("اكتب رابطاً أو نطاقاً. مثال: /url example.com")
        return
    raw = context.args[0].strip()
    candidate = raw if "://" in raw else "https://" + raw
    try:
        parsed = urlparse(candidate)
        host = parsed.hostname
        if not host or not re.fullmatch(r"[A-Za-z0-9.-]+", host) or "." not in host:
            raise ValueError("invalid host")
        warnings = []
        if parsed.scheme != "https":
            warnings.append("الرابط لا يستخدم HTTPS")
        if host.startswith("xn--") or ".xn--" in host:
            warnings.append("النطاق يحتوي على ترميز دولي؛ تحقق من تشابه الحروف")
        if "@" in parsed.netloc:
            warnings.append("يحتوي الجزء الخاص بالمضيف على علامة @")
        result = "مؤشرات تستحق الانتباه: " + "؛ ".join(warnings) if warnings else "لم تظهر مؤشرات شكلية واضحة."
        await update.effective_message.reply_text(f"النطاق: {host}\n{result}\n\nهذا فحص شكلي فقط، وليس فحصاً أمنياً أو حكماً بأن الموقع آمن.")
    except ValueError:
        await update.effective_message.reply_text("الرابط غير واضح. أرسل نطاقاً مثل example.com")

async def lookup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.effective_message.reply_text("اكتب اسم مستخدم عام. مثال: /lookup telegram")
        return
    username = context.args[0].lstrip("@")
    if not re.fullmatch(r"[A-Za-z0-9_]{5,32}", username):
        await update.effective_message.reply_text("اسم المستخدم غير صالح.")
        return
    await update.effective_message.reply_text(f"رابط الحساب العام: https://t.me/{username}\nهذا يفتح صفحة تيليغرام العامة فقط، ولا يكشف الحسابات الخاصة أو المعلومات المخفية.")

def main() -> None:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("phone", phone_command))
    app.add_handler(CommandHandler("url", url_command))
    app.add_handler(CommandHandler("lookup", lookup_command))
    log.info("NANDO FINDER starting")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
