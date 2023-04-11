class TextInput:
    """
    Represents a text input from a user. You can use this class as base to pass additional information to a handler.
    """
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text


class Intention:
    """
    Represents an intention of a user.
    """
    def __init__(self, name: str, examples: list[str]):
        self.name = name
        self.examples = examples

    def __str__(self):
        return f"Intention(name={self.name}, examples={self.examples})"


class IntentionHandler:
    """
    Represents a handler for a specific intention.
    """
    def __call__(self, intention: Intention, text_input: TextInput):
        pass


class IntentionRouter:
    def __init__(self):
        self._handlers = {}

    def get_intentions(self):
        return self._handlers.keys()

    def add_route(self, intention: Intention, handler: IntentionHandler):
        self._handlers[intention] = handler

    def route(self, intention: Intention):
        def decorator(handler: IntentionHandler):
            self._handlers[intention] = handler
            return handler
        return decorator

    def get_handler(self, intention: Intention) -> IntentionHandler:
        return self._handlers[intention]
