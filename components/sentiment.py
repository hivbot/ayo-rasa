from __future__ import annotations

from typing import Dict, Text, Any, List

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.nlu.tokenizers.tokenizer import Token
from rasa.shared.nlu.constants import ENTITIES, TEXT
from rasa.nlu.utils.spacy_utils import SpacyModel, SpacyNLP
from rasa.nlu.extractors.extractor import EntityExtractorMixin

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.downloader.download('vader_lexicon')

import logging

# TODO: Correctly register your component with its type
@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR], is_trainable=False, model_from = "SpacyNLP",
)
class SentimentAnalyzer(GraphComponent, EntityExtractorMixin):
    """Sentiment Analyzer which uses SpaCy."""
    
    def __init__(self, config: Dict[Text, Any]) -> None:
        """Initialize Sentiment Analyzer."""
        self._config = config
    
    @classmethod
    def required_components(cls) -> List[Type]:
        """Components that should be included in the pipeline before this component."""
        return [SpacyNLP]

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """The component's default config (see parent class for full docstring)."""
        return {
            # by default all dimensions recognized by spacy are returned
            # dimensions can be configured to contain an array of strings
            # with the names of the dimensions to filter for
            "dimensions": None
        }
    
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
    def required_packages() -> List[Text]:
        """Lists required dependencies (see parent class for full docstring)."""
        return ["spacy"]


    def train(self, training_data: TrainingData) -> Resource:
       """Not needed, because the the model is pretrained"""
        

    #def process_training_data(self, training_data: TrainingData) -> TrainingData:
        # TODO: Implement this if your component augments the training data with
        #       tokens or message features which are used by other components
        #       during training.
    #    ...

    #    return training_data

    @staticmethod
    def convert_to_rasa(self, value, confidence):
        """Convert model output into the Rasa NLU compatible output format."""
        
        entity = {"value": value,
                  "confidence": confidence,
                  "entity": "sentiment",
                  "extractor": "sentiment_extractor"}

        return entity
        
    
    def process(self, messages: List[Message], model: SpacyModel) -> List[Message]:
        # TODO: This is the method which Rasa Open Source will call during inference.
        logger = logging.getLogger(__name__)
        
            

        for message in messages:
            
            try:
                sid = SentimentIntensityAnalyzer()
                spacy_nlp = model.model
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
                    "confidence": value
                }

                ]
                message.set(
                    "entities", entities, add_to_output=True)
                
                logger.info(message.data)
            except:
                logger.info(message.data)
        
        return messages
    
#    def process(self, message: Message, **kwargs: Any) -> None:
#        print(message.data["text"])
