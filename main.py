import asyncio

from aiogram import Router, Dispatcher, Bot
from aiogram.filters import Command
from aiogram.types import Message

from airouter import intentions
from airouter.dispatcher import IntentionDispatcher
from airouter.openai_utils import init_openai
from airouter.processor import IntentionProcessor
from airouter.router import IntentionRouter, TextInput, IntentionContext, Intention

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

    intention_text, *params_texts = message.text.split('\n')
    # params_texts = '\n'.join(params_texts)

    await message.chat.do('typing')
    text_input = TextInput(intention_text)
    result = await intention_dispatcher.dispatch(text_input)
    if result is not None:
        await message.answer(result)
    else:
        await message.answer('Не удалось распознать намерение')


@intention_router.route(intentions.CREATE_TASK)
async def create_task_handler(intention: Intention, context: IntentionContext, text_input: TextInput):
    return f'create_task ({context.confidence}): {text_input}'


@intention_router.route(intentions.ANSWER_QUESTION)
async def answer_question_handler(intention: Intention, context: IntentionContext, text_input: TextInput):
    return f'answer_question ({context.confidence}): {text_input}'


@intention_router.route(intentions.GIVE_A_JOKE)
async def give_a_joke_handler(intention: Intention, context: IntentionContext, text_input: TextInput):
    return f'give_a_joke ({context.confidence}): {text_input}'


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
