with open("autonomous_trader.py", "r", encoding="utf-8") as f:
    code = f.read()

# Import the notifier
if "from telegram_notifier import TelegramNotifier" not in code:
    code = "from telegram_notifier import TelegramNotifier\n" + code

# Instantiate notifier in __init__
init_target = "        self.trade_size = trade_size"
init_replacement = """        self.trade_size = trade_size
        self.notifier = TelegramNotifier()"""

# Send notification on executed trade
exec_target = '            return {\n                "executed": True,'
exec_replacement = """            # Send push alert
            try:
                alert_msg = (
                    f"🚨 *Arbitrage Executed!*\\n"
                    f"• Strategy: `{direction}`\\n"
                    f"• Spread: `{spread:.4f}`\\n"
                    f"• Size: `{self.trade_size}`\\n"
                    f"• Capital: {cap_res.get('order_id', 'N/A')}\\n"
                    f"• IG: {ig_res.get('order_id', 'N/A')}"
                )
                self.notifier.send_message(alert_msg)
            except Exception as e:
                logger.warning(f"Telegram alert skipped: {e}")

            return {
                "executed": True,"""

code = code.replace(init_target, init_replacement)
code = code.replace(exec_target, exec_replacement)

with open("autonomous_trader.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Wired TelegramNotifier directly into autonomous_trader.py")
