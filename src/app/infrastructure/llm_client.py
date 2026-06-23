import httpx


class LLMClient:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    async def chat(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
