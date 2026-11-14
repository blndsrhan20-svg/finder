import logging
import os
from urllib.parse import urlparse

import phonenumbers
from phonenumbers import PhoneNumberFormat, NumberParseException, PhoneNumberType
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("nando-finder")

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Add it as an environment secret.")

PHONE_TYPES = {
    PhoneNumberType.MOBILE: "موبايل",
    PhoneNumberType.FIXED_LINE: "خط أرضي",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "أرضي أو موبايل",
    PhoneNumberType.TOLL_FREE: "رقم مجاني",
    PhoneNumberType.PREMIUM_RATE: "تعرفة مرتفعة",
    PhoneNumberType.VOIP: "اتصال عبر الإنترنت",
    PhoneNumberType.UNKNOWN: "غير معروف",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"أهلاً {user.first_name or 'بك'} في NANDO FINDER 🔎\n\n"
        "أدوات فحص المعلومات العامة والروابط والأرقام.\n"
        "استخدم /help لمعرفة الأوامر.\n\n"
        "تنبيه: لا أستخرج هوية صاحب رقم أو بيانات حساب خاص، "
        "ولا أستخدم قواعد بيانات مسرّبة."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🔎 أوامر NANDO FINDER\n\n"
        "/id — عرض معرّف حسابك أنت.\n"
        "/phone +9647XXXXXXXXX — فحص صيغة الرقم وبلده ونوعه.\n"
        "/url https://example.com — فحص مؤشرات الرابط المشبوهة.\n"
        "/lookup — توضيح حدود البحث عن معرّفات Telegram.\n\n"
        "لا يمكن معرفة صاحب رقم أو الوصول إلى بيانات خاصة لمجرد إدخال رقم أو ID."
    )


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"معرّف Telegram الخاص بحسابك: {user.id}\n"
        "هذا يعرض معرّفك أنت فقط، ولا يكشف معلومات حسابات الآخرين."
    )


async def phone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("اكتب الرقم مع مفتاح الدولة. مثال: /phone +9647XXXXXXXXX")
        return

    raw_number = " ".join(context.args).strip()
    try:
        number = phonenumbers.parse(raw_number, None)
    except NumberParseException:
        await update.message.reply_text("تعذّر فهم الرقم. استخدم الصيغة الدولية مثل +964...")
        return

    if not phonenumbers.is_possible_number(number):
        await update.message.reply_text("الرقم لا يبدو بطول صحيح.")
        return

    valid = phonenumbers.is_valid_number(number)
    region = phonenumbers.region_code_for_number(number) or "غير محدد"
    kind = PHONE_TYPES.get(phonenumbers.number_type(number), "غير معروف")
    formatted = phonenumbers.format_number(number, PhoneNumberFormat.INTERNATIONAL)
    status = "صالح وفق خطة الترقيم" if valid else "ممكن شكلياً لكن غير مؤكد الصلاحية"
    await update.message.reply_text(
        "📱 فحص الرقم\n"
        f"الرقم: {formatted}\n"
        f"رمز المنطقة: {region}\n"
        f"النوع التقريبي: {kind}\n"
        f"الحالة: {status}\n\n"
        "هذا الفحص لا يحدد اسم المالك أو موقعه أو حساباته."
    )


async def url_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("اكتب الرابط بعد الأمر. مثال: /url https://example.com")
        return

    raw_url = context.args[0].strip()
    candidate = raw_url if "://" in raw_url else "https://" + raw_url
    parsed = urlparse(candidate)
    host = (parsed.hostname or "").lower()
    warnings = []

    if parsed.scheme != "https":
        warnings.append("الرابط لا يستخدم HTTPS.")
    if not host:
        warnings.append("تعذّر استخراج اسم النطاق.")
    if host.startswith("xn--") or ".xn--" in host:
        warnings.append("النطاق يستخدم ترميزاً قد يخفي أحرفاً متشابهة.")
    if "@" in parsed.netloc:
        warnings.append("يحتوي جزء العنوان على @ وقد يكون مضللاً.")
    if host.count("-") >= 3:
        warnings.append("اسم النطاق يحتوي على عدة شرطات.")
    if len(host) > 50:
        warnings.append("اسم النطاق طويل بشكل غير معتاد.")

    if not warnings:
        warnings.append("لم تظهر مؤشرات شكلية بسيطة في الرابط.")

    await update.message.reply_text(
        "🔗 فحص شكلي للرابط\n"
        f"النطاق: {host or 'غير معروف'}\n"
        + "\n".join("• " + item for item in warnings)
        + "\n\nهذا فحص أولي فقط، ولا يضمن أن الموقع آمن. لا تدخل كلمات مرورك عبر روابط مجهولة."
    )


async def lookup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🔍 البحث عن حساب Telegram\n\n"
        "لا يتيح Telegram للبوتات البحث عن صاحب أي ID أو رقم هاتف عشوائي، "
        "ولا يمكنني تجاوز إعدادات الخصوصية أو كشف بيانات مخفية.\n"
        "يمكنني فقط عرض معرّف المستخدم الذي يتفاعل مع البوت، "
        "وفحص معلومات عامة يرسلها المستخدم بنفسه."
    )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("phone", phone_command))
    app.add_handler(CommandHandler("url", url_command))
    app.add_handler(CommandHandler("lookup", lookup_command))
    logger.info("NANDO FINDER is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
