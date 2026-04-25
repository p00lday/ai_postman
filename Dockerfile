# Используем стабильную легкую версию Python
FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Сначала копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем копируем весь остальной код
COPY . .

# Команда старта
CMD ["python", "bot.py"]