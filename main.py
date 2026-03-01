import os
import requests
import re
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# الحصول على توكن البوت من متغير البيئة في Railway
BOT_TOKEN = "8216616214:AAFjBoNImz7MQyvRUREFgGhWt0rJYTdh10c"

# لتتبع المستخدمين الذين أرسلوا زر "فحص رابط"
user_waiting = {}

# رسالة الترحيب والواجهة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 فحص رابط", callback_data="check")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🤖 مرحبًا بك في بوت فلترة تخفيض النقاط Tumo\n\n"
        "نقبل فقط المنتجات التي تحتوي على تخفيض نقاط بين 11% و 24%\n\n"
        "اضغط على الزر للبدء 👇",
        reply_markup=reply_markup
    )

# التعامل مع زر فحص الرابط
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check":
        user_waiting[query.from_user.id] = True
        await query.message.reply_text("📩 أرسل رابط المنتج الآن")

# فحص الرابط والتأكد من تخفيض النقاط
async def check_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_waiting:
        return

    url = update.message.text.strip()
    user_waiting.pop(user_id)

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text().lower()

        # البحث عن نسبة النقاط داخل نص الصفحة
        match = re.search(r'(\d+)%\s*point', text)

        if match:
            discount = int(match.group(1))

            if 11 <= discount <= 24:
                await update.message.reply_text(
                    f"✅ المنتج مقبول\n\n"
                    f"🎯 نسبة تخفيض النقاط: {discount}%\n"
                    f"🔗 الرابط صالح للنشر"
                )
            else:
                await update.message.reply_text(
                    f"❌ نسبة النقاط {discount}% أقل من المطلوب"
                )
        else:
            await update.message.reply_text("❌ لا يوجد تخفيض نقاط في هذا المنتج")

    except:
        await update.message.reply_text("❌ حدث خطأ أثناء فحص الرابط")

# إنشاء التطبيق وإضافة المعالجات
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_link))

# تشغيل البوت
app.run_polling()
