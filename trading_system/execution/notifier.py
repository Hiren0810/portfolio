"""
Multi-Channel Notification Dispatcher.
Broadcasts trade setups, order fills, and risk alerts to Terminal (Rich ANSI),
Discord webhooks, and Telegram bots.
"""

import json
import logging
import urllib.request
import asyncio
from typing import Optional
try:
    from trading_system.core.models import Signal, Order, Position
except (ImportError, ValueError):
    from core.models import Signal, Order, Position

logger = logging.getLogger("Notifier")

class Notifier:
    def __init__(self, discord_webhook: str = "", telegram_token: str = "", telegram_chat_id: str = ""):
        self.discord_webhook = discord_webhook
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id

    def notify_signal(self, signal: Signal):
        """Format and broadcast high-confluence trade signal."""
        emoji = "🚀" if signal.confluence_score > 0 else "🔻"
        header = f"\033[1;36m{emoji} [SIGNAL DETECTED] {signal.symbol} | Direction: {signal.direction.value} | Confluence Score: {signal.confluence_score:+.1f}\033[0m"
        details = (
            f"   Price: ${signal.current_price:.4f} | "
            f"SL: ${signal.suggested_stop_loss:.4f} | "
            f"TP: ${signal.suggested_take_profit:.4f}\n"
            f"   Reasons: {', '.join(signal.reasons[:3])}"
        )
        print(f"{header}\n{details}")

        # Webhook notifications in background
        if self.discord_webhook or (self.telegram_token and self.telegram_chat_id):
            asyncio.create_task(self._send_external_signal(signal))

    def notify_fill(self, order: Order, position: Position):
        """Format and broadcast order fill event."""
        print(f"\033[1;32m✅ [ORDER FILLED] {order.side.value} {order.quantity:.4f} {order.symbol} @ ${order.price:.4f} (Fee: ${order.fee:.4f})\033[0m")

    def notify_exit(self, position: Position):
        """Format and broadcast position closure event."""
        color = "\033[1;32m" if position.realized_pnl >= 0 else "\033[1;31m"
        emoji = "🎯 WIN" if position.realized_pnl >= 0 else "🛑 STOPPED OUT"
        print(f"{color}{emoji} Closed {position.symbol} | PnL: ${position.realized_pnl:+.2f} ({position.unrealized_pnl_pct:+.2f}%) | Reason: {position.close_reason}\033[0m")

    async def _send_external_signal(self, signal: Signal):
        """Dispatch JSON webhook to Discord / Telegram."""
        if self.discord_webhook:
            payload = {
                "embeds": [{
                    "title": f"🚨 Automated Signal: {signal.symbol} ({signal.direction.value})",
                    "color": 65280 if signal.direction.value == "BUY" else 16711680,
                    "fields": [
                        {"name": "Price", "value": f"${signal.current_price:.4f}", "inline": True},
                        {"name": "Confluence Score", "value": f"{signal.confluence_score:+.1f}", "inline": True},
                        {"name": "Stop Loss", "value": f"${signal.suggested_stop_loss:.4f}", "inline": True},
                        {"name": "Take Profit", "value": f"${signal.suggested_take_profit:.4f}", "inline": True},
                        {"name": "Analysis", "value": "\n".join(signal.reasons[:4]), "inline": False}
                    ]
                }]
            }
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._send_http, self.discord_webhook, payload)
            except Exception as e:
                logger.debug(f"Discord webhook failed: {e}")

    def _send_http(self, url: str, data: dict):
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "AntigravityTradingBot"}
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            resp.read()
