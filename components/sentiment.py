from typing import Dict, Text, Any, List

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.constants import TEXT
from rasa.nlu.extractors.extractor import EntityExtractorMixin

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.downloader.download("vader_lexicon")

import logging


@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR], is_trainable=False
)
class SentimentAnalyzer(GraphComponent, EntityExtractorMixin):
    """Sentiment Analyzer."""

    def __init__(self, config: Dict[Text, Any]) -> None:
        """Initialize Sentiment Analyzer."""
        self._config = config

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        """Creates a new component."""
        return cls(config)

    @staticmethod
    def convert_to_rasa(self, value, confidence):
        """Convert model output into the Rasa NLU compatible output format."""

        entity = {
            "value": value,
            "confidence": confidence,
            "entity": "sentiment",
            "extractor": "sentiment_extractor",
        }

        return entity

    def process(self, messages: List[Message]) -> List[Message]:
        logger = logging.getLogger(__name__)

        for message in messages:

            try:
                sid = SentimentIntensityAnalyzer()
                txt = message.get(TEXT)
                res = sid.polarity_scores(txt)

                # vader returns four polarity scores: positive, negative, neutral and compound
                # we will remove compound polarity for the sake of simplicity
                res.pop("compound")

                key, value = max(res.items(), key=lambda x: x[1])

                entities = [
                    {
                        "entity": "sentiment",
                        "extractor": "sentiment_extractor",
                        "value": key,
                        "confidence": value,
                    }
                ]
                message.set("entities", entities, add_to_output=True)

                logger.info(message.data)
            except:
                logger.info(message.data)

        return messages
