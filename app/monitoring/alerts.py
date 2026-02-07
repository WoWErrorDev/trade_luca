from __future__ import annotations

from dataclasses import dataclass

from app.config import AlertsConfig


@dataclass
class Alerts:
    config: AlertsConfig
    logger: object

    def send(self, message: str) -> None:
        if not self.config.telegram_token or not self.config.telegram_chat_id:
            self.logger.info("alert_skipped", extra={"reason": "telegram_not_configured"})
            return
        self.logger.info("alert_sent", extra={"message": message})
