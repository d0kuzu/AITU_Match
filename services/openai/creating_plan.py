import json
import os
import re
from typing import Dict
from openai import AsyncOpenAI

from telegram.misc.texts import GOAL_PLAN_PROMPT

# Инициализация клиента OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
system_messages = [
{"role": "system", "content": "Во время общения по мере необходимости используй текст в тегах <b></b>/<i></i>/<u></u> (жирный/курсивный/подчеркнутый)."},
{"role": "system", "content": "Не пиши слишком много текста."},
{"role": "system", "content": "Обращайся к пользователю по его имени"},
]
system_messages_for_talk = [
{"role": "system", "content": "Когда пользователь доходит до отметок в 1,2,3 недели, не забудь это подметить."},
{"role": "system", "content": "Бери задания из плана в зависимости от текущего дня, из объекта дня в объекте недели."},
{"role": "system", "content": "Пиши не больше 20 слов."},
]


def extract_json_from_text(content: str) -> Dict:
    # Поиск блока, похожего на словарь Python или JSON
    match = content.find("{")
    if match == -1:
        return {"error": "Failed to parse response (not match)", "raw_content": content}

    try:
        obj = json.loads(content[match:])
        return obj
    except json.JSONDecodeError:
        return {"error": "Failed to parse response", "raw_content": content}


async def generate_goal_plan(user_data: Dict) -> Dict:
    prompt = GOAL_PLAN_PROMPT.format(
        name=user_data.get("name", ""),
        goal=user_data.get("goal", ""),
        area=user_data.get("goal_area", ""),
        age=user_data.get("age", ""),
        motivation=user_data.get("motivation", "")
    )
    try:
        response = await client.chat.completions.create(
            model="o3-mini",
            messages=[
                *system_messages,
                {"role": "user", "content": prompt}
            ],
        )
        content = response.choices[0].message.content
        return extract_json_from_text(content)
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


async def ask_question(question: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="o3-mini",
            messages=[
                *system_messages,
                *system_messages_for_talk,
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка запроса: {str(e)}"
