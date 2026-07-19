from app.ml.dataset_loader import DatasetLoader

loader = DatasetLoader(
    "app/ml/dataset/code_review_data_v2.csv"
)

df = loader.load()