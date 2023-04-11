from airouter.router import Intention

CREATE_TASK = Intention(
    'create_task',
    [
        'создай задачу',
        'добавь задачу',
        'задача:',
        'новая задача',
        'добавь в напоминалки'
    ],
)

ANSWER_QUESTION = Intention(
    'answer_question',
    [
        'расскажи историю',
        'ответь на вопрос',
        'расскажи информацию',
        'мне нужна информация',
    ],
)

GIVE_A_JOKE = Intention(
    'answer_question',
    [
        'расскажи анекдот',
        'расскажи шутку',
        'пошути пожалуйста',
        'нужна шутка',
    ],
)
