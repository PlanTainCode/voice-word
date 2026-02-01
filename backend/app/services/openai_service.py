import openai
from app.config import get_settings

settings = get_settings()
client = openai.OpenAI(api_key=settings.openai_api_key)


async def transcribe_audio(file_path: str) -> str:
    """Транскрибация аудио через Whisper API"""
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=audio_file,
            response_format="text"
        )
    return transcript


async def process_text_with_gpt(raw_text: str) -> str:
    """Обработка текста через GPT: проверка слов, пунктуация, абзацы"""
    
    system_prompt = """Ты — профессиональный редактор текста. Твоя задача:

1. Проверить текст на корректность слов по контексту (исправить ошибки распознавания речи)
2. Расставить правильные знаки препинания
3. Разделить текст на логические абзацы
4. Сохранить исходный смысл и стиль речи
5. НЕ добавлять ничего от себя, только редактировать существующий текст

Верни только отредактированный текст без пояснений."""

    response = client.chat.completions.create(
        model=settings.gpt_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Отредактируй следующий текст:\n\n{raw_text}"}
        ],
        temperature=0.3,
        max_completion_tokens=4096
    )
    
    return response.choices[0].message.content

