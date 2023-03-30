from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler,\
    filters, Defaults, CallbackQueryHandler
from telegram.constants import ParseMode
from dotenv import load_dotenv
import os
import logging

from src.utils.db import connect_to_db
from src.constants.commands import START, REGISTER, BACK_TO_MENU, EDIT, QUESTIONS, SKIP_QUESTIONS,\
    QUIT_QUESTIONS, START_QUESTIONS, STAT, BACK_TO_STAT, QUESTIONS_HISTORY,\
    NEXT_QUESTIONS_PAGE, PREV_QUESTIONS_PAGE, ADMIN, REGISTER_ADMIN,\
    ADMIN_SHOW_USERS_LIST, BACK_TO_ADMIN_ACTIONS, ADMIN_PROMPT_ADD_QUESTION_BOX, SHOW_HELP, ADMIN_ADD_HEAD, \
    ADMIN_SHOW_USERS_LIST_BUTTONS, TASK, BACK_TO_TASKS_ACTIONS, REMAINING_TASKS, DONE_TASKS, TOTAL_TASKS_SCORE, \
    TASK_INFORMATION_PREFIX, SUBMIT_TASK_PREFIX, SUBMIT_TASK, HEAD, HEAD_ADD_TASK, BACK_TO_HEAD_ACTIONS,\
    HEAD_SHOW_MARKED_TASKS, HEAD_APPROVE_TASK, HEAD_REMOVE_TASK, HEAD_SHOW_TASKS_TO_REMOVE, \
    REMOVE_QUESTION_BOX_PREFIX, HEAD_SHOW_QUESTIONS_BOX_TO_REMOVE, \
    ADMIN_SHOW_QUESTIONS_BOX_TO_REMOVE, HEAD_SHOW_QUESTION_BOXES_FOR_STAT, \
    GET_QUESTION_BOX_STAT_PREFIX, ADMIN_SHOW_QUESTION_BOXES_FOR_STAT, MENU
from src.constants.other import RegisterMode
from src.constants.states import RegisterStates, EditStates, QuestionStates, StatStates, AdminStates, TaskStates, HeadStates
from src.commands.register import start, ask_for_student_code, register_student_code,\
    register_nickname, register_team
from src.commands.edit import ask_to_edit_what, edit_decider
from src.commands.questions import send_questions, answer_validator,\
    skip_question, quit_questions, prep_phase
from src.commands.admin import show_admin_actions, register_admin, add_question_box, show_users_list, add_head, show_users_list_buttons, admin_decider
from src.commands.task import show_remaining_tasks, show_task_information, show_tasks_actions, show_done_tasks, show_tasks_total_score, mark_task
from src.commands.head import show_head_actions, prompt_add_task, add_task, show_marked_tasks, approve_task, remove_task, show_tasks_to_remove, show_questions_box_to_remove, remove_question_box, show_question_boxes_for_stat, show_question_box_stat_and_percent
from src.commands.stat import stat_decider, get_user_stat, show_question_box_stat
from src.commands.other import questions_history, back_to_menu, show_help, cleaner

# loads .env content into env variables
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
program_mode = os.getenv("MODE")


def main():
    defaults = Defaults(parse_mode=ParseMode.HTML,
                        block=False, disable_notification=True)

    application = ApplicationBuilder().token(
        BOT_TOKEN).post_init(connect_to_db).defaults(defaults).build()

    start_handler = CommandHandler(START, start)
    menu_handler = CommandHandler(MENU, back_to_menu)

    register_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        entry_points=[CallbackQueryHandler(
            ask_for_student_code, REGISTER)],
        states={
            RegisterStates.REGISTER_STUDENT_CODE: [CallbackQueryHandler(back_to_menu, BACK_TO_MENU), MessageHandler(filters.TEXT, register_student_code(RegisterMode.CREATE))],
            RegisterStates.REGISTER_TEAM: [CallbackQueryHandler(back_to_menu, BACK_TO_MENU), CallbackQueryHandler(register_team(RegisterMode.CREATE))],
            RegisterStates.REGISTER_NICKNAME: [CallbackQueryHandler(back_to_menu, BACK_TO_MENU),
                                               MessageHandler(
                filters.TEXT, register_nickname(RegisterMode.CREATE))]
        },
        fallbacks=[CallbackQueryHandler(back_to_menu, BACK_TO_MENU)]
    )

    edit_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        entry_points=[CallbackQueryHandler(ask_to_edit_what, EDIT)],
        states={
            EditStates.EDIT_DECIDER: [CallbackQueryHandler(back_to_menu, BACK_TO_MENU), CallbackQueryHandler(edit_decider)],
            EditStates.EDIT_STUDENT_CODE: [MessageHandler(
                filters.TEXT, register_student_code(RegisterMode.EDIT))],
            EditStates.EDIT_NICKNAME: [MessageHandler(
                filters.TEXT, register_nickname(RegisterMode.EDIT))],
            EditStates.EDIT_TEAM: [CallbackQueryHandler(
                register_team(RegisterMode.EDIT))]
        },
        fallbacks=[CallbackQueryHandler(back_to_menu, BACK_TO_MENU)]
    )

    question_handler = ConversationHandler(
        per_message=True,
        per_chat=True,
        per_user=True,
        entry_points=[CallbackQueryHandler(prep_phase, QUESTIONS)],
        states={
            QuestionStates.SHOW_QUESTIONS: [CallbackQueryHandler(send_questions, START_QUESTIONS), CallbackQueryHandler(back_to_menu, BACK_TO_MENU)],
            QuestionStates.ANSWER_VALIDATOR: [CallbackQueryHandler(skip_question, SKIP_QUESTIONS),
                                              CallbackQueryHandler(
                                                  quit_questions, QUIT_QUESTIONS),
                                              CallbackQueryHandler(answer_validator)],
        },
        fallbacks=[CallbackQueryHandler(back_to_menu, BACK_TO_MENU)]
    )

    stat_handler = ConversationHandler(
        per_message=True,
        per_chat=True,
        per_user=True,
        entry_points=[CallbackQueryHandler(get_user_stat, STAT)],
        states={
            StatStates.SHOW_STAT: [CallbackQueryHandler(get_user_stat)],
            StatStates.SELECT_QUESTION_BOX: [
                CallbackQueryHandler(back_to_menu, BACK_TO_MENU),
                CallbackQueryHandler(show_question_box_stat)],
            StatStates.DECIDER: [CallbackQueryHandler(stat_decider, BACK_TO_STAT),
                                 CallbackQueryHandler(back_to_menu, BACK_TO_MENU)]
        },
        fallbacks=[CallbackQueryHandler(back_to_menu, BACK_TO_MENU)]
    )

    admin_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        entry_points=[CallbackQueryHandler(
            show_admin_actions, ADMIN), CommandHandler(ADMIN, show_admin_actions)],
        states={
            AdminStates.SHOW_ADMIN_ACTIONS: [CallbackQueryHandler(back_to_menu, BACK_TO_MENU), CallbackQueryHandler(show_admin_actions, BACK_TO_ADMIN_ACTIONS)],
            AdminStates.REGISTER_USER_AS_AN_ADMIN: [
                CallbackQueryHandler(register_admin, REGISTER_ADMIN)],
            AdminStates.ADMIN_ACTIONS: [CallbackQueryHandler(show_users_list_buttons, ADMIN_SHOW_USERS_LIST_BUTTONS),
                                        CallbackQueryHandler(
                                            show_users_list, ADMIN_SHOW_USERS_LIST),
                                        CallbackQueryHandler(
                                            back_to_menu, BACK_TO_MENU),
                                        CallbackQueryHandler(show_questions_box_to_remove(
                                            for_admin=True), ADMIN_SHOW_QUESTIONS_BOX_TO_REMOVE),
                                        CallbackQueryHandler(remove_question_box(
                                            for_admin=True), REMOVE_QUESTION_BOX_PREFIX),
                                        CallbackQueryHandler(
                                            show_admin_actions, BACK_TO_ADMIN_ACTIONS),
                                        MessageHandler(
                                            filters.Document.Category(
                                                'application/json'),
                                            add_question_box(for_admin=True)),
                                        CallbackQueryHandler(
                                            back_to_menu, BACK_TO_MENU),
                                        CallbackQueryHandler(
                                            add_question_box(for_admin=True), ADMIN_PROMPT_ADD_QUESTION_BOX),
                                        CallbackQueryHandler(show_question_boxes_for_stat(
                                            for_admin=True), ADMIN_SHOW_QUESTION_BOXES_FOR_STAT),
                                        CallbackQueryHandler(show_question_box_stat_and_percent(
                                            for_admin=True), GET_QUESTION_BOX_STAT_PREFIX)
                                        ],
            AdminStates.ADMIN_DECIDER: [CallbackQueryHandler(admin_decider)],
            AdminStates.ADD_HEAD: [CallbackQueryHandler(
                back_to_menu, BACK_TO_MENU), CallbackQueryHandler(add_head)]
        },
        fallbacks=[]
    )

    task_handler = ConversationHandler(
        per_chat=True,
        per_user=True,
        per_message=True,
        entry_points=[CallbackQueryHandler(show_tasks_actions, TASK)],
        states={
            TaskStates.SHOW_TASKS_ACTIONS: [CallbackQueryHandler(show_tasks_actions, BACK_TO_TASKS_ACTIONS)],
            TaskStates.TASK_ACTION_DECIDER: [CallbackQueryHandler(show_tasks_actions, BACK_TO_TASKS_ACTIONS),
                                             CallbackQueryHandler(
                                                 show_remaining_tasks(TASK_INFORMATION_PREFIX, "این تموم تسک هایی که برات گذاشتن", without_mark=False), REMAINING_TASKS),
                                             CallbackQueryHandler(
                                                 show_done_tasks, DONE_TASKS),
                                             CallbackQueryHandler(
                                                 show_tasks_total_score, TOTAL_TASKS_SCORE),
                                             CallbackQueryHandler(
                                                 show_task_information, TASK_INFORMATION_PREFIX),
                                             CallbackQueryHandler(
                                                 mark_task, SUBMIT_TASK_PREFIX),
                                             CallbackQueryHandler(show_remaining_tasks(
                                                 SUBMIT_TASK_PREFIX, "تسک هایی که میتونی ثبت کنی", without_mark=True), SUBMIT_TASK),
                                             ],
        },
        fallbacks=[CallbackQueryHandler(back_to_menu, BACK_TO_MENU)]
    )

    head_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(show_head_actions, HEAD)],
        states={
            HeadStates.HEAD_ACTION_DECIDER: [
                CallbackQueryHandler(add_question_box(
                    for_admin=False), ADMIN_PROMPT_ADD_QUESTION_BOX),
                MessageHandler(filters.Document.Category(
                    "application/json"), add_question_box(for_admin=False)),
                CallbackQueryHandler(show_questions_box_to_remove(
                    for_admin=False), HEAD_SHOW_QUESTIONS_BOX_TO_REMOVE),
                CallbackQueryHandler(remove_question_box(
                    for_admin=False), REMOVE_QUESTION_BOX_PREFIX),
                CallbackQueryHandler(prompt_add_task, HEAD_ADD_TASK),
                CallbackQueryHandler(
                    show_marked_tasks, HEAD_SHOW_MARKED_TASKS),
                CallbackQueryHandler(approve_task, HEAD_APPROVE_TASK),
                CallbackQueryHandler(show_tasks_to_remove,
                                     HEAD_SHOW_TASKS_TO_REMOVE),
                CallbackQueryHandler(remove_task, HEAD_REMOVE_TASK),
                CallbackQueryHandler(
                    show_question_boxes_for_stat(for_admin=False), HEAD_SHOW_QUESTION_BOXES_FOR_STAT),
                CallbackQueryHandler(
                    show_question_box_stat_and_percent(for_admin=False), GET_QUESTION_BOX_STAT_PREFIX)
            ],
            HeadStates.HEAD_ADD_TASK: [MessageHandler(
                filters.Document.Category("application/json"), add_task)]
        },
        fallbacks=[CallbackQueryHandler(
            show_head_actions, BACK_TO_HEAD_ACTIONS), CallbackQueryHandler(back_to_menu, BACK_TO_MENU)]
    )

    history_handlers = [
        CommandHandler(QUESTIONS_HISTORY, questions_history),
        CallbackQueryHandler(questions_history, QUESTIONS_HISTORY),
        CallbackQueryHandler(questions_history, NEXT_QUESTIONS_PAGE),
        CallbackQueryHandler(questions_history, PREV_QUESTIONS_PAGE)
    ]

    back_to_menu_handler = CallbackQueryHandler(back_to_menu, BACK_TO_MENU)
    show_help_handler = CallbackQueryHandler(show_help, SHOW_HELP)

    application.add_handler(start_handler)
    application.add_handler(menu_handler)
    application.add_handler(task_handler)
    application.add_handler(head_handler)
    application.add_handler(admin_handler)
    application.add_handler(register_handler)
    application.add_handler(edit_handler)
    application.add_handler(question_handler)
    application.add_handler(stat_handler)
    application.add_handler(back_to_menu_handler)
    application.add_handler(show_help_handler)
    application.add_handler(MessageHandler(
        filters.ALL & (~filters.COMMAND), cleaner))

    application.add_handlers(history_handlers)

    if program_mode.lower() == 'production':
        application.run_webhook(
            listen="",
            port=8443,
            secret_token=os.getenv("BOT_SECRET"),
            key="private.key",
            cert="cert.pem",
            webhook_url="https://amirhossein-mazaheri.ir:8443"
        )
    else:
        application.run_polling()


if __name__ == '__main__':
    main()
