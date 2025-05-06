import logging
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
    "t1": ("Взаємне розміщення прямих у просторі", None, """<b>1. Перетинаються</b>
- Мають одну спільну точку.
- Лежать в одній площині.
- Кут між прямими — це кут між напрямними векторами.

<b>2. Паралельні</b>
- Не перетинаються, але в одній площині.
- Колінеарні напрямні вектори.
- Відстань між прямими стала.

<b>3. Збігаються</b>
- Нескінченно багато спільних точок.
- Це одна і та сама пряма.
- Вектори однієї — кратні вектору іншої.

<b>4. Скрещуються</b>
- Немає жодної спільної точки.
- Не лежать в одній площині.
- Приклад — ребра прямокутного паралелепіпеда."""),

    "t2": ("Взаємне розміщення прямої і площини", None, """<b>1. Пряма лежить у площині</b>
- Усі точки прямої належать площині.
- Напрямний вектор належить площині.

<b>2. Перетинає площину</b>
- Єдина точка перетину.
- Не лежить у площині.
- Вектор не колінеарний площині.

<b>3. Паралельна площині</b>
- Не має спільних точок.
- Вектор прямої паралельний площині."""),

    "t3": ("Формули і геометричні умови", None, """- Перевірка скрещування: векторне та змішане добутки.
- Перетин прямої і площини: <i>A + tv</i> та нормаль площини <i>n</i>."""),

    "t4": ("Взаємне розміщення площин у просторі", "image4.jpg", """- <b>Перетинаються</b>: мають спільну пряму.
- <b>Паралельні</b>: не мають спільних точок або збігаються.

<b>Властивості:</b>
1. Перетин третьою площиною — дає паралельні прямі.
2. Відрізки між площинами рівні."""),

    "t5": ("Паралельність прямих в площин у просторі", "image5.jpg", """- Не мають спільних точок.
- Колінеарні вектори.
- Лежать в одній площині.
- Вектор не перпендикулярний площині.
- Має одну точку перетину."""),

    "t6": ("Паралельність двох площин", "image6.jpg", """- Ознака: прямі з площини A паралельні прямим у площині B.

<b>Властивості:</b>
1. Прямі перетину з третьою площиною — паралельні.
2. Відрізки між площинами рівні."""),

    "t7": ("Властивості паралельних прямих у просторі", "image7.jpg", """- Прямі з паралельних площин, перетнутих третьою — паралельні.
- Якщо обидві прямі паралельні третій — вони паралельні між собою.""")
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
    await query.answer()
    topic_key = query.data

    if topic_key not in topics:
        await query.edit_message_text("Обрано невірну тему.")
        return MENU

    name, img_filename, description = topics[topic_key]
    text = f"<b>{name}</b>\n\n{description}"

    keyboard = [[InlineKeyboardButton("◀️ Повернутись до тем", callback_data="start_learning")]]

    if img_filename:
        with open(f"images/{img_filename}", "rb") as photo:
            await query.message.reply_photo(
                photo=photo,
                caption=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

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
            states={
    MENU: [
        CallbackQueryHandler(menu, pattern="^start_learning$"),
        CallbackQueryHandler(show_topic, pattern="^t[1-7]$"),
        CallbackQueryHandler(start_quiz, pattern="^quiz$")
    ],
    TOPIC: [
        CallbackQueryHandler(menu, pattern="^start_learning$")  # <== добавлено сюда
    ],
    QUIZ: [
        CommandHandler("cancel", cancel),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)
    ],
},


    app.add_handler(conv_handler)
    logger.info("Бот запущено")
    app.run_polling()
