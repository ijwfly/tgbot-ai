import asyncio

from aiogram import Router, Dispatcher, Bot
from aiogram.filters import Command
from aiogram.types import Message

from airouter import intentions
from airouter.dispatcher import IntentionDispatcher
from airouter.openai_utils import init_openai
from airouter.processor import IntentionProcessor
from airouter.router import IntentionRouter, TextInput

OPENAI_API_KEY = ''
TELEGRAM_TOKEN = ''
TELEGRAM_ADMIN_ID = 0

router = Router()
intention_router = IntentionRouter()
intention_processor = IntentionProcessor()
intention_dispatcher = IntentionDispatcher(intention_router, intention_processor)


@router.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        return
    await message.answer(f"Привет, <b>{message.from_user.full_name}!</b>")


@router.message()
async def message_handler(message: Message) -> None:
    if message.from_user.id != TELEGRAM_ADMIN_ID:
        return

    text_input = TextInput(message.text)
    result = await intention_dispatcher.dispatch(text_input)

    await message.answer(result)


@intention_router.route(intentions.CREATE_TASK)
async def create_task_handler(intention, text_input):
    return f'create_task: {text_input}'


@intention_router.route(intentions.ANSWER_QUESTION)
async def answer_question_handler(intention, text_input):
    return f'answer_question: {text_input}'


@intention_router.route(intentions.GIVE_A_JOKE)
async def give_a_joke_handler(intention, text_input):
    return f'give_a_joke: {text_input}'


async def main():
    init_openai(OPENAI_API_KEY)
    await intention_dispatcher.build()

    dp = Dispatcher()
    dp.include_router(router)
    bot = Bot(TELEGRAM_TOKEN, parse_mode="HTML")
    print('Starting polling...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
