import io
import logging
import urllib.parse
from io import BytesIO
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Your Telegram Bot Token
BOT_TOKEN = "8831091538:AAGv75PDytTewlViu21VnnuKYAqfUcf3l7Y"

# Developer Info & Payment Setup
DEVELOPER_NAME = "Sheikh Atiq Hasan"
BKASH_NAGAD_NUMBER = "01767045665"  # আপনার বিকাশ/নগদ নাম্বার বসান
TELEGRAM_USERNAME = "@atiqhasan65"  # আপনার টেলিগ্রাম আইডি বসান

# Dictionary to track daily user usage
user_usage = {}
DAILY_LIMIT = 5


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  welcome_text = (
      f"👋 Welcome to Atiq AI Image Generator Bot!\n"
      f"Developed by: {DEVELOPER_NAME}\n\n"
      "Send me any text prompt, and I will generate a high-quality AI image for"
      " you.\n\n"
      f"🎁 Free Daily Limit: {DAILY_LIMIT} images/day.\n"
      "Type /status to check your remaining limit."
  )
  await update.message.reply_text(welcome_text)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  used = user_usage.get(user_id, 0)
  remaining = max(0, DAILY_LIMIT - used)
  await update.message.reply_text(
      f"📊 Your Usage Status:\nUsed today: {used}/{DAILY_LIMIT}\nRemaining free"
      f" images: {remaining}"
  )


async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  prompt = update.message.text

  # Initialize user counter if not present
  if user_id not in user_usage:
    user_usage[user_id] = 0

  # Check daily limit
  if user_usage[user_id] >= DAILY_LIMIT:
    payment_message = (
        "⚠️ You have reached your daily limit of 5 free images!\n\n"
        "💎 Upgrade to Premium for Unlimited Images:\n"
        "💳 Fee: BDT 100 / Month\n"
        f"📱 bKash / Nagad Personal: {BKASH_NAGAD_NUMBER}\n\n"
        "📩 Send payment screenshot for instant activation to:\n"
        f"Developer: {DEVELOPER_NAME}\n"
        f"Telegram: {TELEGRAM_USERNAME}"
    )
    await update.message.reply_text(payment_message)
    return

  # Send waiting status
  msg = await update.message.reply_text(
      "🎨 Generating your AI image... Please wait a few seconds."
  )

  try:
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

    response = requests.get(image_url)

    if response.status_code == 200:
      image_bytes = BytesIO(response.content)
      image_bytes.name = "generated_image.jpg"

      # Send generated photo to user
      await update.message.reply_photo(
          photo=image_bytes, caption=f"✨ Prompt: {prompt}"
      )
      user_usage[user_id] += 1
      await msg.delete()
    else:
      await msg.edit_text("❌ Failed to generate image. Please try again later.")

  except Exception as e:
    await msg.edit_text("❌ An error occurred while generating the image.")


def main():
  app = ApplicationBuilder().token(BOT_TOKEN).build()

  app.add_handler(CommandHandler("start", start))
  app.add_handler(CommandHandler("status", status))
  app.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image)
  )

  print("🤖 Telegram Bot is running...")
  app.run_polling()


if __name__ == "__main__":
  main()