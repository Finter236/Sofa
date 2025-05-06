import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ConversationHandler, ContextTypes, MessageHandler, filters
)

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Стан бота
MENU, TOPIC, QUIZ = range(3)

# Теми
topic_ids = {
    "t1": "Взаємне розміщення прямих у просторі",
    "t2": "Взаємне розміщення прямої і площини",
    "t3": "Формули і геометричні умови",
    "t4": "Взаємне розміщення площин у просторі",
    "t5": "Паралельність прямих в площин у просторі",
    "t6": "Паралельність двох площин",
    "t7": "Властивості паралельних прямих у просторі"
}

topics = {
    "t1": """<b>1. Взаємне розміщення прямих у просторі</b>

<b>Перетинаються</b>
- Прямі a і b мають одну спільну точку.
- Існує площина, в якій вони обидві лежать.
- Кут між прямими можна знайти як кут між їхніми напрямними векторами.

<b>Паралельні</b>
- Прямі a і b не перетинаються, але лежать в одній площині.
- Їхні напрямні вектори колінеарні.
- Відстань між прямими залишається сталою.

<b>Збігаються</b>
- Прямі мають нескінченно багато спільних точок.
- Фактично — це одна і та сама пряма.
- Усі вектори однієї прямої можна виразити як множення вектора іншої на скаляр.

<b>Скрещуються (мимобіжні)</b>
- Прямі не мають жодної спільної точки.
- Не лежать в одній площині.
- Приклад у реальному житті: ребра різних граней прямокутного паралелепіпеда.""",

    "t2": """<b>2. Взаємне розміщення прямої і площини</b>

<b>Пряма лежить у площині</b>
- Всі точки прямої належать площині.
- Вектор прямої належить площині, а також початкова точка прямої лежить у площині.

<b>Пряма перетинає площину</b>
- Єдина спільна точка — точка перетину.
- Пряма не лежить у площині.
- Її напрямний вектор не є колінеарним жодному з векторів, які лежать у площині.

<b>Пряма паралельна площині</b>
- Не має жодної спільної точки з площиною.
- Її напрямний вектор паралельний площині.
- Пряма і площина не мають спільних точок, але не перетинаються.""",

    "t3": """<b>3. Формули і геометричні умови</b>

- Перевірка скрещування:
  Якщо прямі не перетинаються і не лежать в одній площині — вони мимобіжні.
  Це можна перевірити через векторне та змішане добутки.

- Перетин прямої і площини:
  Якщо точка A прямої і напрямний вектор v⃗, а площина задана точкою P і нормальним вектором n⃗, то точка перетину задовольняє рівняння.""",

    "t4": ("<b>4. Взаємне розміщення площин у просторі</b>", "image4.jpg", """<b>Перетинаються</b>: мають спільну пряму.
<b>Паралельні</b>: не мають спільних точок або збігаються.

<b>Властивості:</b>
1. Якщо дві паралельні площини перетинаються третьою, то прямі перетину паралельні.
2. Відрізки паралельних прямих, які містяться між паралельними площинами, рівні."""),

    "t5": ("<b>5. Паралельність прямих в площині у просторі</b>", "image5.jpg", """- Не мають спільних точок у площині.
- Їхні напрямні вектори колінеарні.
- Прямі лежать в одній площині.
- Прямі не перетинаються.
- Вектор прямої не перпендикулярний площині.
- Мають лише одну точку перетину (у випадку перетинання)."""),

    "t6": ("<b>6. Паралельність двох площин</b>", "image6.jpg", """<b>Ознака:</b> 
Якщо дві прямі, що перетинаються і лежать у площині α, відповідно паралельні двом прямим, які перетинаються і лежать у площині β, то ці площини паралельні.

<b>Властивості:</b>
1. Якщо дві паралельні площини перетинаються третьою, то прямі перетину паралельні.
2. Відрізки паралельних прямих, які містяться між паралельними площинами, рівні."""),

    "t7": ("<b>7. Властивості паралельних прямих у просторі</b>", "image7.jpg", """- Прямі, одержані при перетині двох паралельних площин третьою, паралельні між собою.
- Дві прямі, кожна з яких паралельна третій, паралельні між собою.""")
}

quiz_questions = {
    "t1": ("Яка ознака того, що прямі перетинаються?", "мають одну спільну точку"),
    "t2": ("Коли пряма лежить у площині?", "усі точки прямої належать площині"),
    "t3": ("Як перевірити скрещування прямих?", "векторне та змішане добутки"),
    "t4": ("Яка умова перетину площин?", "мають спільну пряму"),
    "t5": ("Ознака паралельності прямих?", "вектори колінеарні"),
    "t6": ("Коли площини паралельні?", "прямі паралельні в обох площинах"),
    "t7": ("Коли дві прямі паралельні між собою?", "обидві паралельні третій прямій")
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("▶️ Почати навчання", callback_data="start_learning")]]
    await update.message.reply_text(
        "Привіт! Я бот для вивчення геометрії. Натисни кнопку ⬇️",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(topic_ids[tid], callback_data=tid)] for tid in topic_ids]
    keyboard.append([InlineKeyboardButton("✅ Все вивчив!", callback_data="quiz")])
    await query.edit_message_text("Оберіть тему для вивчення:", reply_markup=InlineKeyboardMarkup(keyboard))
    return MENU

async def show_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    topic_key = query.data
    topic_data = topics[topic_key]

    # Якщо дані — це просто текст (старі теми)
    if isinstance(topic_data, str):
        text = f"<b>{topic_ids[topic_key]}</b>\n\n{topic_data}"
        await query.message.reply_text(text, parse_mode="HTML")
    else:
        # Якщо дані — кортеж (нові теми з зображенням)
        name, img_filename, description = topic_data
        text = f"<b>{name}</b>\n\n{description}"
        with open(f"images/{img_filename}", "rb") as photo:
            await query.message.reply_photo(photo=photo, caption=text, parse_mode="HTML")

    return TOPIC


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['quiz'] = iter(quiz_questions.items())
    context.user_data['wrong'] = []
    return await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tid, (question, answer) = next(context.user_data['quiz'])
        context.user_data['current_q'] = (tid, answer)

        text = f"🧠 {question}\n\n(Напишіть відповідь у повідомленні)"
        if update.callback_query:
            await update.callback_query.edit_message_text(text)
        else:
            await update.message.reply_text(text)

        return QUIZ

    except StopIteration:
        wrong = context.user_data.get('wrong', [])
        if wrong:
            wrong_list = "\n".join(f"🔹 {topic_ids[tid]}" for tid in wrong)
            text = f"Переглянь ці теми ще раз:\n{wrong_list}"
        else:
            text = "🎉 Вітаю! Усі відповіді правильні."

        # Проверка: откуда пришел апдейт — сообщение или колбэк
        if update.callback_query:
            await update.callback_query.edit_message_text(text)
        else:
            await update.message.reply_text(text)

        return ConversationHandler.END


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.strip().lower()
    tid, correct_answer = context.user_data['current_q']
    if correct_answer.lower() not in user_answer:
        context.user_data['wrong'].append(tid)
    return await ask_question(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Навчання завершено. Щасти!")
    return ConversationHandler.END

if __name__ == '__main__':
    app = Application.builder().token("8125962066:AAHi-aHXVfddpUyfxmsbVpVhjO_XEUH6tCE").build()

    conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        MENU: [
            CallbackQueryHandler(menu, pattern="^start_learning$"),
            CallbackQueryHandler(show_topic, pattern="^t[1-7]$"),
            CallbackQueryHandler(start_quiz, pattern="^quiz$")
        ],
        TOPIC: [
            CallbackQueryHandler(menu, pattern="^start_learning$"),
            # можна додати більше callbackів, якщо потрібно
        ],
        QUIZ: [
            CommandHandler("cancel", cancel),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_chat=True  # ✅ важлива опція
)


    app.add_handler(conv_handler)
    logger.info("Бот запущено")
    app.run_polling()

