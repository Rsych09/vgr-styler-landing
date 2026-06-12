# main.py
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI(title="Dropshipping Lead API v1.1")

# Настройка CORS полиси (разрешаем нашему лендингу слать запросы к бэкенду)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # На продакшене лучше указать точный адрес твоего сайта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- НАСТРОЙКИ ТЕЛЕГРАМ-БОТА ---
BOT_TOKEN = "8450030881:AAG3u9j0k1I7dyrSIOGWOiBNG7nmEaxKae0"
CHAT_ID = "6516874857"

class LeadModel(BaseModel):
    name: str
    phone: str
    product: str

@app.post("/api/leads")
async def create_lead(lead: LeadModel):
    # Форматируем текст, который прилетит в Telegram-чат
    message = (
        "🔔 **НОВЫЙ ЗАКАЗ НА САЙТЕ!** 🔔\n\n"
        f"🔥 **Продукт:** {lead.product}\n"
        f"👤 **Имя клиента:** {lead.name}\n"
        f"📞 **Телефон:** `{lead.phone}`\n\n"
        "⚡️ Скорее свяжись с клиентом, пока он горячий!"
    )
    
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    # Асинхронно отправляем данные в API Телеграма
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(telegram_url, json=payload, timeout=10.0)
            
            # Если Телеграм вернул ошибку, выводим её подробности в терминал VS Code
            if response.status_code != 200:
                print(f"\n❌ ОШИБКА TELEGRAM API: Статус {response.status_code}")
                print(f"📝 Ответ от Telegram: {response.text}")
                print("💡 Справка: Если написано 'Forbidden: bot can't initiate conversation with a user', значит ты забыл зайти в бот и нажать кнопку СТАРТ (/start).\n")
                raise HTTPException(status_code=500, detail="Ошибка при отправке в Telegram API")
                
        except httpx.RequestError as exc:
            print(f"\n❌ ОШИБКА СЕТИ: Не удалось связаться с серверами Telegram: {exc}\n")
            raise HTTPException(status_code=500, detail="Ошибка соединения с Telegram")
            
    print(f"\n✅ ЗАЯВКА УСПЕШНО ОТПРАВЛЕНА: {lead.name} ({lead.phone})\n")
    return {"status": "success", "message": "Заявка успешно обработана и отправлена"}


from fastapi.staticfiles import StaticFiles
# Раздаем всю текущую папку (индекс и картинки). Важно: эта строка должна быть ниже всех @app.post/get маршрутов!
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# Запуск сервера в правильном формате модуля для Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)