import subprocess

class OllamaLLM:
    def __init__(self, model="deepseek-coder"):
        self.model = model

    def generate(self, prompt):
        try:
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt.encode("utf-8"),
                capture_output=True,
                check=True
            )
            return result.stdout.decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            return f"[OllamaLLM Error] {e.stderr.decode('utf-8').strip()}"
        except Exception as e:
            return f"[OllamaLLM Error] {str(e)}"
