from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from prisma.models import QuestionOption

from src.constants.other import LAST_MESSAGE_KEY


async def show_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE, question: str, options: list[QuestionOption]):
    keyboard = InlineKeyboardMarkup(
        list(map(lambda option: [InlineKeyboardButton(option.label, callback_data=option.id)], options)))

    text = (
        "<b>Answer The Question</b>\n\n"
        f"{question}"
    )

    sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=keyboard)
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id
