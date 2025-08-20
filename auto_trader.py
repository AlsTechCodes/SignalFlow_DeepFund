import asyncio
import os
from datetime import datetime, time
from dotenv import load_dotenv
from utils.telegram_bot import TelegramNotifier
from utils.trade_executor import TradeExecutor
from main import run_hedge_fund

# Load environment variables
load_dotenv()

class AutoTrader:
    def __init__(self, tickers: list[str], initial_cash: float = 100000.0):
        """Initialize the automated trading system."""
        self.tickers = tickers
        self.portfolio = {
            'cash': initial_cash,
            'positions': {},
            'margin_requirement': 0.0
        }
        
        # Initialize Telegram bot if credentials are available
        self.telegram = None
        if os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'):
            self.telegram = TelegramNotifier()
        
        self.trade_executor = TradeExecutor(self.portfolio, self.telegram)

    async def run_trading_cycle(self):
        """Run a single trading cycle."""
        try:
            # Get current date
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # Run the hedge fund analysis
            result = run_hedge_fund(
                tickers=self.tickers,
                start_date=current_date,
                end_date=current_date,
                portfolio=self.portfolio,
                show_reasoning=True,
                selected_analysts=['ben_graham', 'warren_buffett', 'technical_analyst', 'sentiment'],
                model_name="gpt-4",
                model_provider="OpenAI"
            )

            # Execute the trading decisions
            if result and result.get('decisions'):
                await self.trade_executor.execute_portfolio_decisions(result['decisions'])

        except Exception as e:
            error_msg = f"Error in trading cycle: {str(e)}"
            if self.telegram:
                await self.telegram.send_error(error_msg)
            print(error_msg)

    async def run(self, trading_hours_start: time = time(9, 30), trading_hours_end: time = time(16, 0)):
        """Run the automated trading system during market hours."""
        if self.telegram:
            await self.telegram.send_signal(
                ticker="SYSTEM",
                action="START",
                quantity=0,
                price=0,
                confidence=100,
                reasoning="Automated trading system started"
                
            )

        while True:
            current_time = datetime.now().time()
            
            # Check if we're within trading hours
            if trading_hours_start <= current_time <= trading_hours_end:
                await self.run_trading_cycle()
                # Wait for 5 minutes before next cycle
                await asyncio.sleep(300)
            else:
                # Outside trading hours, wait until next trading day
                if current_time > trading_hours_end:
                    # Wait until next trading day
                    await asyncio.sleep(3600)  # Check every hour
                else:
                    # Wait until market open
                    await asyncio.sleep(300)  # Check every 5 minutes

async def main():
    # Example usage
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    trader = AutoTrader(tickers=tickers, initial_cash=100000.0)
    await trader.run()

if __name__ == "__main__":
    asyncio.run(main()) 