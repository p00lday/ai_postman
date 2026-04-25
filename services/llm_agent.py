from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from config import Config

# Настройка модели Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=Config.GOOGLE_API_KEY
)

async def filter_and_summarize(news_item, user_topics):
    """
    Универсальный промпт-фильтр: 
    Решает, нужна ли новость Степану, и делает выжимку.
    """
    prompt = f"""
    Ты — профессиональный ИИ-редактор новостей для Степана.
    Его список интересов: {", ".join(user_topics)}
    
    Вот новость:
    {news_item}
    
    Задание:
    1. Если новость НЕ относится к темам Степана — ответь только одним словом: SKIP.
    2. Если новость релевантна — напиши:
       - 📌 Краткую суть (2-3 тезиса).
       - 💡 Почему это важно для его интересов.
    
    Отвечай строго на русском языке.
    """
    
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        return f"Ошибка AI: {e}"