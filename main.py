import functions_framework
from app import telegram_webhook

@functions_framework.http
def handle_telegram(request):
    return telegram_webhook(request)