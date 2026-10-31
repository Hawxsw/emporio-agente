import json

import anthropic
from anthropic import beta_tool

from src.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from src.prompts import build_system_prompt
from src.tools import TOOLS

FALLBACK_REPLY = "Opa, não consegui formular uma resposta agora. Pode repetir de outro jeito?"


class StoreAgent:
    def __init__(self, history: list[dict] | None = None):
        if not ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set. Create the .env file (see .env.example).")
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, max_retries=4)
        self.tools = {tool.name: tool for tool in map(beta_tool, TOOLS)}
        self.system = build_system_prompt()
        self.messages = history or []

    def _run_tool(self, block) -> dict:
        try:
            result = self.tools[block.name].call(block.input)
        except Exception as error:
            return {"type": "tool_result", "tool_use_id": block.id, "content": f"Error: {error}", "is_error": True}
        if not isinstance(result, str):
            result = json.dumps(result, ensure_ascii=False)
        return {"type": "tool_result", "tool_use_id": block.id, "content": result}

    def reply(self, message: str) -> str:
        messages = [*self.messages, {"role": "user", "content": message}]
        while True:
            response = self.client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=16000,
                system=self.system,
                tools=[tool.to_dict() for tool in self.tools.values()],
                output_config={"effort": "low"},
                cache_control={"type": "ephemeral"},
                messages=messages,
            )
            content = [block.model_dump(mode="json", exclude_none=True) for block in response.content]
            messages.append({"role": "assistant", "content": content})
            if response.stop_reason != "tool_use":
                break
            results = [self._run_tool(block) for block in response.content if block.type == "tool_use"]
            messages.append({"role": "user", "content": results})

        self.messages = messages
        text = "".join(block.text for block in response.content if block.type == "text")
        return text or FALLBACK_REPLY

    def history(self) -> list[dict]:
        return self.messages
