from airouter.processor import IntentionProcessor
from airouter.router import IntentionRouter, TextInput


class IntentionDispatcher:
    def __init__(self, router: IntentionRouter, processor: IntentionProcessor):
        self.router = router
        self.processor = processor

    def initialized(self):
        return self.processor.initialized()

    async def build(self):
        await self.processor.build(self.router.get_intentions())

    async def dispatch(self, text_input: TextInput):
        if not self.initialized():
            raise ValueError('Intention dispatcher is not initialized')
        intention = await self.processor.process(text_input.text)
        handler = self.router.get_handler(intention)
        return await handler(intention, text_input)
