"""
inference.py - AI Inference Engine
===================================
Wraps the model to tokenize prompts, run generation,
and decode outputs. Supports both Seq2Seq and CausalLM models.
"""


class CodeT5Inference:
    """Handles tokenization, generation, and decoding using a language model."""

    def __init__(self, model, tokenizer):
        """
        Args:
            model:     A HuggingFace model.
            tokenizer: The matching AutoTokenizer.
        """
        self.model = model
        self.tokenizer = tokenizer
        # Check if model is a decoder-only model (Causal LM)
        self.is_causal = "CausalLM" in type(model).__name__

    def generate(self, prompt, max_length=256, system_prompt=None):
        """
        Generate improved code from a prompt.

        Args:
            prompt:        The instruction + source code prompt string.
            max_length:    Maximum number of tokens in the generated output.
            system_prompt: Optional custom system instructions.

        Returns:
            The decoded generated text.
        """
        try:
            # For Causal LM, we should construct a proper chat prompt if it's Qwen Instruct
            if self.is_causal and "Qwen" in type(self.model).__name__:
                sys_content = system_prompt or "You are a helpful assistant that improves Python code. Respond ONLY with the improved Python code block. Do not write explanation or markdown code block fences."
                messages = [
                    {"role": "system", "content": sys_content},
                    {"role": "user", "content": prompt}
                ]
                formatted_prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            else:
                formatted_prompt = prompt

            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
            )

            # Generate
            if self.is_causal:
                output_ids = self.model.generate(
                    inputs["input_ids"],
                    max_new_tokens=max_length,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                # Slice out prompt tokens
                generated_ids = output_ids[0][inputs["input_ids"].shape[1]:]
            else:
                output_ids = self.model.generate(
                    inputs["input_ids"],
                    num_beams=4,
                    max_length=max_length,
                    early_stopping=True,
                )
                generated_ids = output_ids[0]

            generated_text = self.tokenizer.decode(
                generated_ids,
                skip_special_tokens=True,
            )
            
            # Clean up markdown code block backticks if present
            if "```python" in generated_text:
                generated_text = generated_text.split("```python")[1].split("```")[0]
            elif "```" in generated_text:
                generated_text = generated_text.split("```")[1].split("```")[0]
                
            return generated_text.strip()

        except Exception as e:
            print(f"[CodeT5Inference] Generation failed: {e}")
            return self._extract_code_from_prompt(prompt)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_code_from_prompt(prompt):
        """
        Best-effort extraction of the raw source code from the prompt.
        """
        parts = prompt.split(":\n", 1)
        return parts[-1] if len(parts) > 1 else prompt
