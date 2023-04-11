from dataclasses import dataclass
from typing import List

import numpy as np

from airouter.openai_utils.embedding import vector_similarity, get_embeddings, EmbeddedText
from airouter.router import Intention


@dataclass
class EmbeddedIntention:
    intention: Intention
    embedded_examples: List[EmbeddedText] = None

    def initialized(self):
        return self.embedded_examples is not None

    def avg_embedding(self):
        if not self.initialized():
            raise ValueError('Embedded intention is not initialized')
        embeddings = [example.embedding for example in self.embedded_examples]
        return np.mean(embeddings, axis=0).tolist()

    async def build(self):
        examples = self.intention.examples
        self.embedded_examples = await get_embeddings(examples)


class IntentionProcessor:
    def __init__(self):
        self._intentions = None
        self._embedded_intentions = None

    def initialized(self):
        return self._embedded_intentions is not None

    async def build(self, intentions):
        self._intentions = intentions
        self._embedded_intentions = [
            EmbeddedIntention(intention)
            for intention in intentions
        ]
        for embedded_intention in self._embedded_intentions:
            await embedded_intention.build()

    async def process(self, text: str) -> Intention:
        if not self.initialized():
            raise ValueError('Intention processor is not initialized')

        embedded_text = await get_embeddings([text])
        embedded_text = embedded_text[0]
        similarities = []
        for embedded_intention in self._embedded_intentions:
            avg_embedding = embedded_intention.avg_embedding()
            similarity = vector_similarity(avg_embedding, embedded_text.embedding)
            similarities.append(similarity)
        max_similarity = max(similarities)
        max_similarity_index = similarities.index(max_similarity)
        return self._embedded_intentions[max_similarity_index].intention
