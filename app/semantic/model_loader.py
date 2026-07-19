from transformers import AutoTokenizer, AutoModel
import torch


class ModelLoader:
    _model = None
    _tokenizer = None

    @classmethod
    def load_model(cls):
        if cls._model is None:
            print("Loading CodeBERT model...")

            model_name = "microsoft/codebert-base"

            cls._tokenizer = AutoTokenizer.from_pretrained(model_name)
            cls._model = AutoModel.from_pretrained(model_name)

            print("[SUCCESS] CodeBERT Loaded Successfully!")

        return cls._model, cls._tokenizer   