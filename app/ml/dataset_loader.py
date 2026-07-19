"""
Dataset Loader for CodeSearchNet (Python)

Loads the official CodeSearchNet dataset and returns
Python functions for feature extraction.
"""

from datasets import load_dataset


class DatasetLoader:

    def __init__(self):
        self.dataset = None

    def load_train_dataset(self):
        """Load training dataset"""
        self.dataset = load_dataset(
            "claudios/code_search_net",
            "python",
            split="train"
        )
        return self.dataset

    def load_validation_dataset(self):
        """Load validation dataset"""
        return load_dataset(
            "claudios/code_search_net",
            "python",
            split="validation"
        )

    def load_test_dataset(self):
        """Load test dataset"""
        return load_dataset(
            "claudios/code_search_net",
            "python",
            split="test"
        )

    def get_code_samples(self, limit=100):
        """
        Return first N code samples.
        """
        if self.dataset is None:
            self.load_train_dataset()

        samples = []

        for item in self.dataset.select(range(limit)):
            samples.append({
                "function_name": item["func_name"],
                "code": item["func_code_string"],
                "documentation": item["func_documentation_string"],
                "repository": item["repository_name"]
            })

        return samples