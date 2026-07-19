from transformers import AutoTokenizer, AutoModelForCausalLM


class ModelLoader:

    def __init__(self):
        # We use Qwen2.5-Coder-0.5B-Instruct as it is a state-of-the-art lightweight coding model
        # capable of zero-shot instructions-based code editing, which the base CodeT5 model cannot do.
        model_name = "Qwen/Qwen2.5-Coder-0.5B-Instruct"

        print(f"Loading AI model: {model_name}...")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

        print("Model Loaded Successfully!")

    def get_model(self):
        return self.model, self.tokenizer