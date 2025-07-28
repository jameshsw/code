import openai
import json
from pydantic import BaseModel, ValidationError

class CodeResponse(BaseModel):
    code: str

prompt = "Write a Python function that returns the square of a number. Return only a JSON object with a 'code' field containing the function as a string."

client = openai.OpenAI(
    api_key="EMPTY",
    base_url="http://localhost:8000/v1",
)

SCHEMA = {
    "type": "object",
    "properties": {
        "code": {"type": "string"},
    },
    "required": ["code"],
}

messages = [
    {"role": "user", "content": prompt}
]
chat_completion = client.chat.completions.create(
    messages=messages,
    model="Qwen/Qwen3-1.7B",
    response_format={
        "type": "json_object",
        "schema": CodeResponse.model_json_schema(),
    },
    max_tokens=128,
    temperature=0.7,
)

print("Content:", chat_completion.choices[0].message.content)

# Validate with Pydantic
try:
    data = json.loads(chat_completion.choices[0].message.content)
    parsed = CodeResponse(**data)
    print("Validated code:", parsed.code)
except (json.JSONDecodeError, ValidationError) as e:
    print("Failed to parse/validate model output:", e)