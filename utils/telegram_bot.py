import os
from telegram import Bot
from telegram.error import TelegramError
from typing import Dict, Optional
from datetime import datetime

class TelegramNotifier:
    def __init__(self, token: Optional[str] = None):
        """Initialize the Telegram bot with the provided token or from environment."""
        self.token = token or os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("Telegram bot token not provided and not found in environment variables")
        self.bot = Bot(token=self.token)
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not self.chat_id:
            raise ValueError("Telegram chat ID not provided and not found in environment variables")

    async def send_signal(self, ticker: str, action: str, quantity: int, price: float, confidence: float, reasoning: str):
        """Send a trading signal to the configured Telegram chat."""
        try:
            message = (
                f"🔔 Trading Signal Alert\n\n"
                f"Ticker: {ticker}\n"
                f"Action: {action.upper()}\n"
                f"Quantity: {quantity}\n"
                f"Price: ${price:.2f}\n"
                f"Confidence: {confidence:.1f}%\n"
                f"Reasoning: {reasoning}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await self.bot.send_message(chat_id=self.chat_id, text=message)
        except TelegramError as e:
            print(f"Failed to send Telegram message: {e}")

    async def send_portfolio_update(self, portfolio: Dict):
        """Send a portfolio update to the configured Telegram chat."""
        try:
            message = (
                f"📊 Portfolio Update\n\n"
                f"Cash: ${portfolio.get('cash', 0):.2f}\n"
                f"Positions:\n"
            )
            
            for ticker, position in portfolio.get('positions', {}).items():
                message += f"{ticker}: {position['shares']} shares @ ${position.get('avg_price', 0):.2f}\n"
            
            message += f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            await self.bot.send_message(chat_id=self.chat_id, text=message)
        except TelegramError as e:
            print(f"Failed to send Telegram message: {e}")

    async def send_error(self, error_message: str):
        """Send an error message to the configured Telegram chat."""
        try:
            message = (
                f"⚠️ Error Alert\n\n"
                f"Message: {error_message}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await self.bot.send_message(chat_id=self.chat_id, text=message)
        except TelegramError as e:
            print(f"Failed to send Telegram message: {e}") 