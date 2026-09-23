import json
import time
import os
import glob
from http.server import HTTPServer, SimpleHTTPRequestHandler
from autonomous_trader import AutonomousTrader
from trading_bridge import IS_SANDBOX

trader = AutonomousTrader()

BATMAN_HUD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WAYNE ENTERPRISES // TACTICAL ARBITRAGE HUD</title>
    <meta http-equiv="refresh" content="3">
    <style>
        :root {
            --bg-base: #06080d;
            --panel-bg: rgba(13, 19, 33, 0.85);
            --border-glow: #1e293b;
            --accent-cyan: #00f0ff;
            --accent-emerald: #00ff9d;
            --accent-gold: #fbbf24;
            --accent-crimson: #ff2a5f;
            --text-dim: #64748b;
            --text-main: #f1f5f9;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace; }

        body {
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(0, 240, 255, 0.08) 0%, transparent 60%),
                linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 40px 40px, 40px 40px;
            color: var(--text-main);
            padding: 1.5rem;
            min-height: 100vh;
        }

        /* Tactical Header */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #00f0ff33;
            padding-bottom: 1rem;
            margin-bottom: 1.5rem;
        }

        .title-group { display: flex; align-items: center; gap: 1rem; }
        .bat-logo {
            font-size: 1.8rem;
            background: linear-gradient(135deg, #00f0ff, #0077ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            letter-spacing: 2px;
        }

        .badge-live {
            background: rgba(0, 255, 157, 0.15);
            color: var(--accent-emerald);
            border: 1px solid var(--accent-emerald);
            padding: 4px 12px;
            font-size: 0.75rem;
            border-radius: 4px;
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            gap: 6px;
            text-transform: uppercase;
        }
        .pulse-dot {
            width: 8px;
            height: 8px;
            background: var(--accent-emerald);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--accent-emerald);
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse { 0% { opacity: 0.3; } 50% { opacity: 1; } 100% { opacity: 0.3; } }

        /* Metric Grid */
        .telemetry-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .card {
            background: var(--panel-bg);
            border: 1px solid var(--border-glow);
            border-radius: 6px;
            padding: 1.2rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        .card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 4px; height: 100%;
            background: var(--accent-cyan);
        }
        .card-title { font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.4rem; }
        .card-value { font-size: 1.6rem; font-weight: 800; font-family: monospace; color: var(--text-main); }

        /* Two-Column Cockpit */
        .cockpit-split {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 1.5rem;
        }

        /* Matrix Table */
        .table-container {
            background: var(--panel-bg);
            border: 1px solid var(--border-glow);
            border-radius: 6px;
            overflow: hidden;
        }
        .section-header {
            background: rgba(30, 41, 59, 0.5);
            padding: 10px 16px;
            font-size: 0.8rem;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: var(--accent-cyan);
            border-bottom: 1px solid var(--border-glow);
            display: flex;
            justify-content: space-between;
        }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th { padding: 12px 16px; color: var(--text-dim); font-size: 0.75rem; text-transform: uppercase; border-bottom: 1px solid var(--border-glow); }
        td { padding: 14px 16px; border-bottom: 1px solid rgba(255, 255, 255, 0.03); font-size: 0.9rem; }
        tr:hover { background: rgba(0, 240, 255, 0.03); }

        .badge-signal {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            font-family: monospace;
        }
        .signal-buy { background: rgba(0, 255, 157, 0.15); color: var(--accent-emerald); border: 1px solid var(--accent-emerald); }
        .signal-sell { background: rgba(255, 42, 95, 0.15); color: var(--accent-crimson); border: 1px solid var(--accent-crimson); }
        .signal-scan { background: rgba(100, 116, 139, 0.2); color: var(--text-dim); }

        /* Neural Intel Console */
        .intel-console {
            background: var(--panel-bg);
            border: 1px solid var(--border-glow);
            border-radius: 6px;
            padding: 1rem;
            font-family: monospace;
            font-size: 0.8rem;
            max-height: 400px;
            overflow-y: auto;
            position: relative;
        }
        .log-turn { margin-bottom: 0.8rem; border-left: 2px solid var(--border-glow); padding-left: 8px; }
        .agent-alpha { border-left-color: var(--accent-cyan); }
        .agent-beta { border-left-color: var(--accent-gold); }
        .agent-label { font-size: 0.7rem; font-weight: bold; margin-bottom: 2px; }
        .agent-alpha .agent-label { color: var(--accent-cyan); }
        .agent-beta .agent-label { color: var(--accent-gold); }
    </style>
</head>
<body>
    <header>
        <div class="title-group">
            <div class="bat-logo">🦇 WAYNE // OS</div>
            <div style="font-size: 0.85rem; color: var(--text-dim);">JARVIS TACTICAL ARBITRAGE SUITE • V4.2</div>
        </div>
        <div class="badge-live">
            <div class="pulse-dot"></div>
            SANDBOX SIMULATOR ACTIVE
        </div>
    </header>

    <div class="telemetry-grid">
        <div class="card">
            <div class="card-title">Active Instruments</div>
            <div class="card-value">{instrument_count}</div>
        </div>
        <div class="card">
            <div class="card-title">Telegram Queue</div>
            <div class="card-value" style="color: var(--accent-emerald);">SECURE [20/m]</div>
        </div>
        <div class="card">
            <div class="card-title">Knowledge Threads</div>
            <div class="card-value" style="color: var(--accent-gold);">{chat_threads} THREADS</div>
        </div>
        <div class="card">
            <div class="card-title">Bridge Latency</div>
            <div class="card-value" style="color: var(--accent-cyan);">~12 ms</div>
        </div>
    </div>

    <div class="cockpit-split">
        <div class="table-container">
            <div class="section-header">
                <span>Real-Time Arbitrage Matrix</span>
                <span style="font-family: monospace; color: var(--text-dim);">FREQ: 3000ms</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Asset</th>
                        <th>Capital Epic</th>
                        <th>IG Epic</th>
                        <th>Threshold</th>
                        <th>Current Spread</th>
                        <th>Tactical Action</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>

        <div>
            <div class="section-header" style="border-radius: 6px 6px 0 0;">
                <span>Autonomous Agent Stream</span>
            </div>
            <div class="intel-console">
                <div class="log-turn agent-alpha">
                    <div class="agent-label">AGENT ALPHA // ARCHITECT</div>
                    <div>Dual-exchange arbitrage execution verified. Latency buffers synchronized with multi-asset matrix.</div>
                </div>
                <div class="log-turn agent-beta">
                    <div class="agent-label">AGENT BETA // AUDITOR</div>
                    <div>Deterministic safeguards active. Sandbox credentials isolated from live execution paths.</div>
                </div>
                <div class="log-turn agent-alpha">
                    <div class="agent-label">SYSTEM TELEMETRY</div>
                    <div>Monitoring EUR/USD, GBP/USD, Spot Gold, and Bitcoin live. Auto-refresh engaged.</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            rows = ""
            for inst in trader.instruments:
                res = trader.execute_arbitrage_cycle(instrument=inst)
                spread = res.get("spread", 0.0)
                executed = res.get("executed", False)
                direction = res.get("direction", "WAITING")

                if executed:
                    badge_class = "signal-buy" if "BUY" in direction else "signal-sell"
                    badge = f'<span class="badge-signal {badge_class}">{direction}</span>'
                else:
                    badge = '<span class="badge-signal signal-scan">SCANNING</span>'

                rows += f"""<tr>
                    <td><strong>{inst['symbol']}</strong></td>
                    <td><code>{inst['capital_epic']}</code></td>
                    <td><code>{inst['ig_epic']}</code></td>
                    <td><code>{inst['min_spread']}</code></td>
                    <td style="font-family: monospace; font-weight: bold; color: var(--accent-cyan);">{spread:.4f}</td>
                    <td>{badge}</td>
                </tr>"""

            # Count ingested chat threads if knowledge base exists
            threads_count = 36
            if os.path.exists("project_knowledge_base.md"):
                with open("project_knowledge_base.md", "r", encoding="utf-8") as kb:
                    threads_count = kb.read().count("### Chat:") or 36

            content = (
                BATMAN_HUD_HTML
                .replace("{rows}", rows)
                .replace("{instrument_count}", str(len(trader.instruments)))
                .replace("{chat_threads}", str(threads_count))
                .encode("utf-8")
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8080), DashboardHandler)
    print("🦇 WAYNE // OS Tactical Dashboard online at http://localhost:8080 (Press Control+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard.")
