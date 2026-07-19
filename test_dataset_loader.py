from app.ml.dataset_loader import DatasetLoader

loader = DatasetLoader()

loader.load_train_dataset()

samples = loader.get_code_samples(5)

for i, sample in enumerate(samples, start=1):
    print("=" * 60)
    print(f"Sample {i}")
    print("=" * 60)
    print("Function:", sample["function_name"])
    print("Repository:", sample["repository"])
    print("Documentation:", sample["documentation"])
    print("\nCode:\n")
    print(sample["code"])
    print()