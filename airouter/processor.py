import itertools
from dataclasses import dataclass
from typing import List

import numpy as np

from airouter.openai_utils.embedding import vector_similarity, get_embeddings, EmbeddedText
from airouter.router import Intention, IntentionContext


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

    def avg_inner_similarity(self):
        if not self.initialized():
            raise ValueError('Embedded intention is not initialized')
        avg_embedding = self.avg_embedding()
        similarities = [vector_similarity(avg_embedding, example.embedding) for example in self.embedded_examples]
        return np.mean(similarities)

    async def build(self):
        examples = self.intention.examples
        self.embedded_examples = await get_embeddings(examples)


class IntentionValidator:
    def __init__(self, intentions: List[EmbeddedIntention]):
        self.intentions = intentions

    def check_intersection(self):
        errors = []
        for intention_1, intention_2 in itertools.combinations(self.intentions, 2):
            i1_avg_embedding = intention_1.avg_embedding()
            i1_avg_inner_similarity = intention_1.avg_inner_similarity()
            for example in intention_2.embedded_examples:
                similarity = vector_similarity(i1_avg_embedding, example.embedding)
                if similarity >= i1_avg_inner_similarity:
                    error_text = f'Intention "{intention_1.intention.name}" and "{intention_2.intention.name}" ' \
                                 f'have intersection in example "{example.text}"'
                    errors.append(error_text)
        return errors

    def check_round_shape(self):
        errors = []
        for intention in self.intentions:
            avg_embedding = intention.avg_embedding()
            avg_inner_similarity = intention.avg_inner_similarity()
            for example in intention.embedded_examples:
                similarity = vector_similarity(avg_embedding, example.embedding)
                if similarity < avg_inner_similarity * 0.75:
                    error_text = f'Intention "{intention.intention.name}" doesnt have round shape in ' \
                                 f'example "{example.text}" - similarity: {similarity}, avg_inner_similarity: {avg_inner_similarity}'
                    errors.append(error_text)
        return errors

    def validate(self):
        intersection_errors = self.check_intersection()
        round_shape_errors = self.check_round_shape()
        return intersection_errors + round_shape_errors


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

        errors = IntentionValidator(self._embedded_intentions).validate()
        if errors:
            raise ValueError('Intention errors: ', errors)

    async def process(self, text: str):
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
        return self._embedded_intentions[max_similarity_index].intention, IntentionContext(max_similarity)
