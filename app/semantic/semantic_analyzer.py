import torch

from .model_loader import ModelLoader
from .feature_extractor import FeatureExtractor


class SemanticAnalyzer:

    def __init__(self):
        self.model, self.tokenizer = ModelLoader.load_model()

    def analyze(self, code):

        inputs = self.tokenizer(
            code,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        return FeatureExtractor.extract(outputs)