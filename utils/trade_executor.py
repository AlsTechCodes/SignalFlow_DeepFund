import asyncio
from typing import Dict, Optional
from datetime import datetime
import yfinance as yf
from .telegram_bot import TelegramNotifier

class TradeExecutor:
    def __init__(self, portfolio: Dict, telegram_notifier: Optional[TelegramNotifier] = None):
        """Initialize the trade executor with a portfolio and optional Telegram notifier."""
        self.portfolio = portfolio
        self.telegram = telegram_notifier
        self.pending_orders = {}

    async def execute_trade(self, ticker: str, action: str, quantity: int, confidence: float, reasoning: str):
        """Execute a trade and update the portfolio."""
        try:
            # Get current price
            stock = yf.Ticker(ticker)
            current_price = stock.info.get('regularMarketPrice', 0)
            
            if current_price == 0:
                raise ValueError(f"Could not get current price for {ticker}")

            # Calculate trade value
            trade_value = current_price * quantity

            # Execute the trade based on action
            if action == "buy":
                if trade_value > self.portfolio['cash']:
                    raise ValueError(f"Insufficient cash for buy order: ${trade_value:.2f} > ${self.portfolio['cash']:.2f}")
                
                # Update portfolio
                self.portfolio['cash'] -= trade_value
                if ticker not in self.portfolio['positions']:
                    self.portfolio['positions'][ticker] = {'shares': 0, 'avg_price': 0}
                
                current_position = self.portfolio['positions'][ticker]
                total_shares = current_position['shares'] + quantity
                total_cost = (current_position['shares'] * current_position['avg_price']) + trade_value
                current_position['avg_price'] = total_cost / total_shares
                current_position['shares'] = total_shares

            elif action == "sell":
                if ticker not in self.portfolio['positions'] or self.portfolio['positions'][ticker]['shares'] < quantity:
                    raise ValueError(f"Insufficient shares for sell order: {quantity} > {self.portfolio['positions'].get(ticker, {}).get('shares', 0)}")
                
                # Update portfolio
                self.portfolio['cash'] += trade_value
                self.portfolio['positions'][ticker]['shares'] -= quantity
                if self.portfolio['positions'][ticker]['shares'] == 0:
                    del self.portfolio['positions'][ticker]

            elif action == "short":
                margin_required = trade_value * 0.5  # 50% margin requirement
                if margin_required > self.portfolio['cash']:
                    raise ValueError(f"Insufficient margin for short order: ${margin_required:.2f} > ${self.portfolio['cash']:.2f}")
                
                # Update portfolio
                self.portfolio['cash'] -= margin_required
                if ticker not in self.portfolio['positions']:
                    self.portfolio['positions'][ticker] = {'shares': 0, 'avg_price': 0}
                
                current_position = self.portfolio['positions'][ticker]
                current_position['shares'] -= quantity  # Negative shares indicate short position
                current_position['avg_price'] = current_price

            elif action == "cover":
                if ticker not in self.portfolio['positions'] or self.portfolio['positions'][ticker]['shares'] > -quantity:
                    raise ValueError(f"Insufficient short position for cover order: {quantity} > {abs(self.portfolio['positions'].get(ticker, {}).get('shares', 0))}")
                
                # Update portfolio
                self.portfolio['cash'] -= trade_value
                self.portfolio['positions'][ticker]['shares'] += quantity
                if self.portfolio['positions'][ticker]['shares'] == 0:
                    del self.portfolio['positions'][ticker]

            # Send notification if Telegram bot is configured
            if self.telegram:
                await self.telegram.send_signal(
                    ticker=ticker,
                    action=action,
                    quantity=quantity,
                    price=current_price,
                    confidence=confidence,
                    reasoning=reasoning
                )
                await self.telegram.send_portfolio_update(self.portfolio)

            return True

        except Exception as e:
            error_msg = f"Error executing {action} order for {ticker}: {str(e)}"
            if self.telegram:
                await self.telegram.send_error(error_msg)
            raise ValueError(error_msg)

    async def execute_portfolio_decisions(self, decisions: Dict):
        """Execute multiple trading decisions from the portfolio manager."""
        for ticker, decision in decisions.items():
            if decision['action'] != 'hold':
                await self.execute_trade(
                    ticker=ticker,
                    action=decision['action'],
                    quantity=decision['quantity'],
                    confidence=decision['confidence'],
                    reasoning=decision['reasoning']
                ) 