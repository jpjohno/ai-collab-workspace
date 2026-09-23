import time
import yaml
from bridge.socket_server import NativeSocketBridge
from strategy.soft_arb_engine import SoftArbEngine
from risk.circuit_breaker import RiskCircuitBreaker
from utils.logger import logger

def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def handle_mt4_message(msg, engine, risk_breaker, config):
    msg_type = msg.get("type")

    if msg_type == "TICK":
        tick_count = getattr(handle_mt4_message, "count", 0) + 1
        handle_mt4_message.count = tick_count
        if tick_count % 25 == 0:
            logger.info(f"[MT4 LIVE FEED] {msg.get('symbol')} | Bid: {msg.get('bid')} Ask: {msg.get('ask')}")

        signal = engine.process_tick(msg)
        if signal and not risk_breaker.is_halted:
            logger.info(f"[STRATEGY TRIGGER] Momentum Spike: {signal}")
            return {"status": "EXECUTE", "signal": signal}

        return {"status": "ACK"}

    elif msg_type == "ACCOUNT":
        equity = float(msg.get("equity", 0.0))
        risk_breaker.set_starting_equity(equity)
        risk_breaker.check_pnl_limit(equity)
        return {"status": "ACK", "halted": risk_breaker.is_halted}

    return {"status": "ACK"}

def main():
    logger.info("Initializing Soft-Arbitrage Native Bridge...")
    config = load_config()

    bridge_cfg = config.get("bridge", {})
    strat_cfg = config.get("strategy", {})
    risk_cfg = config.get("risk", {})

    bridge = NativeSocketBridge(
        host=bridge_cfg.get("host", "127.0.0.1"),
        port=bridge_cfg.get("port", 5555)
    )
    engine = SoftArbEngine(
        target_pip_win=strat_cfg.get("target_pip_win", 1.2),
        max_stop_loss=strat_cfg.get("max_stop_loss", 4.8),
        impulse_threshold=strat_cfg.get("impulse_pip_trigger", 4.0)
    )
    risk_breaker = RiskCircuitBreaker(
        max_daily_drawdown_pct=risk_cfg.get("max_daily_drawdown_percent", 3.0),
        max_slippage_pips=risk_cfg.get("max_slippage_pips", 0.3)
    )

    bridge.start()
    logger.info("[ENGINE ACTIVE] Listening for Pepperstone MT4 ticks on port 5555...")

    try:
        while True:
            bridge.poll_and_process(
                lambda msg: handle_mt4_message(msg, engine, risk_breaker, config),
                timeout_ms=10
            )
            time.sleep(0.001)
    except KeyboardInterrupt:
        logger.info("Shutting down engine...")
    finally:
        bridge.stop()

if __name__ == "__main__":
    main()
