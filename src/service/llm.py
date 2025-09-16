from typing import List, Dict
import aiohttp
from src.config import settings

MessageHistory = List[Dict[str, str]]

# ✅ OpenRouter endpoint
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {settings.LLM_TOKEN}",
    "Content-Type": "application/json",
}


async def llm_request(messages: MessageHistory, model: str = "deepseek/deepseek-chat", max_tokens: int = 500, temperature: float = 1.2):
    payload = {
        "model": model,   # 👈 можно менять модель: "deepseek/deepseek-chat", "openai/gpt-4o-mini", "mistralai/mistral-7b-instruct"
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, headers=HEADERS, json=payload) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                print(f"❌ Ошибка API OpenRouter: {resp.status} - {error_text}")
                return "У Джохи сейчас технические шоколадки 😅 Попробуй позже."
            data = await resp.json()
            print("--- OpenRouter API Response ---")
            print(data)
            return data["choices"][0]["message"]["content"]


async def llm_init_agent() -> str:
    initial_messages = [
        {
            "role": "system",
            "content": (
                "Тебя зовут Джоха. Ты острый на язык и иронию парень 21 год, "
                "и ты общаешься со студентами. "
                "Ты должен изящно и тонко высмеивать их в диалоге. "
                "Используй тот факт, что они пользуются ботом для знакомств (какая жалость) и общаются с ИИ. "
                "Ты всегда представляешься как Джоха. "
                "Ты общаешься неформально и очень кратко, МАКСИМАЛЬНО кратко, как в переписке. "
                "Никогда не извиняйся и не будь вежливым, всегда стебай собеседника."
            ),
        },
        {"role": "user", "content": "Привет! Мне никто не пишет..."},
    ]
    return await llm_request(initial_messages, max_tokens=330, temperature=1.4)


async def llm_generate_simple(text: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "Ты Джоха. Острый на язык, 21 год. "
                "Троллишь студентов, которые сидят в боте знакомств. "
                "Неформально, очень кратко, без извинений."
            ),
        },
        {"role": "user", "content": text},
    ]
    return await llm_request(messages)


async def llm_generate(history: MessageHistory, user_text: str, max_context_messages: int = 10) -> str:
    current_messages = list(history)
    current_messages.append({"role": "user", "content": user_text})

    # ограничим историю
    if len(current_messages) > max_context_messages:
        current_messages = current_messages[-max_context_messages:]

    return await llm_request(current_messages, max_tokens=1000, temperature=1.2)
