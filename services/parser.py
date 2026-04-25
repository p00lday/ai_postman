import requests
from bs4 import BeautifulSoup

# Список проверенных лент
RSS_FEEDS = [
    "https://habr.com/ru/rss/news/",                # IT/Общее
    "https://3dnews.ru/news/rss/",                  # Мини-ПК и Железо
    "https://www.ixbt.com/export/news.rss",         # Технологии
    "https://ria.ru/export/rss2/space/index.xml",      # Космос (РИА)
    "https://naked-science.ru/feed",                # Космос и Наука
    "https://www.ferra.ru/exports/rss.xml",         # Гаджеты
    "https://tass.ru/rss/v2.xml"                    # Главные новости (для фильтрации ЧАЗН)
]

def get_latest_news(limit_per_feed=10):
    all_news = []
    
    for url in RSS_FEEDS:
        try:
            # Имитируем браузер, чтобы сайты не блокировали запрос
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, features="xml")
            items = soup.find_all("item")[:limit_per_feed]
            
            for item in items:
                title = item.find("title").text if item.find("title") else ""
                link = item.find("link").text if item.find("link") else ""
                desc = item.find("description").text if item.find("description") else ""
                
                # Собираем данные в один блок для Gemini
                clean_text = f"ИСТОЧНИК: {url}\nЗАГОЛОВОК: {title}\nОПИСАНИЕ: {desc}\nССЫЛКА: {link}"
                all_news.append(clean_text)
                
        except Exception as e:
            # Если одна лента упала, просто идем к следующей
            continue
            
    return "\n\n---\n\n".join(all_news)