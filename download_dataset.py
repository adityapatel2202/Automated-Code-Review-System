from datasets import load_dataset

print("Downloading dataset...")

dataset = load_dataset(
    "claudios/code_search_net",
    "python",
    split="train"
)

print(dataset)
print(dataset[0])