from openai import OpenAI

import config

client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)

response = client.chat.completions.create(
    model=config.LLM_MODEL,
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
    temperature=0.3,
    reasoning_effort=config.REASONING_EFFORT,
    **{config.TOKEN_LIMIT_PARAM: 100},
)
print("model:", config.LLM_MODEL)
print("answer:", response.choices[0].message.content)
print("finish_reason:", response.choices[0].finish_reason)
