import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from autonomous_trader import AutonomousTrader

trader = AutonomousTrader()

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Arbitrage Matrix Dashboard</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; }
        h1 { color: #38bdf8; margin-bottom: 0.5rem; }
        p.subtitle { color: #94a3b8; margin-top: 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 1.5rem; background: #1e293b; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px 16px; text-align: left; }
        th { background: #334155; color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; }
        tr { border-bottom: 1px solid #334155; }
        tr:last-child { border-bottom: none; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.75rem; }
        .badge-buy { background: #065f46; color: #34d399; }
        .badge-sell { background: #991b1b; color: #f87171; }
        .badge-wait { background: #374151; color: #9ca3af; }
    </style>
</head>
<body>
    <h1>Arbitrage Matrix Dashboard</h1>
    <p class="subtitle">Live Scanning • Sandbox Mode Active • Auto-refreshes every 3s</p>
    <table>
        <thead>
            <tr>
                <th>Instrument</th>
                <th>Capital Epic</th>
                <th>IG Epic</th>
                <th>Spread Threshold</th>
                <th>Last Spread</th>
                <th>Status / Action</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
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
                    badge = f'<span class="badge badge-buy">{direction}</span>'
                else:
                    badge = '<span class="badge badge-wait">MONITORING</span>'

                rows += f"""<tr>
                    <td><strong>{inst['symbol']}</strong></td>
                    <td><code>{inst['capital_epic']}</code></td>
                    <td><code>{inst['ig_epic']}</code></td>
                    <td>{inst['min_spread']}</td>
                    <td><code>{spread:.4f}</code></td>
                    <td>{badge}</td>
                </tr>"""

            content = HTML_PAGE.replace("{rows}", rows).encode("utf-8")
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
    print("🌐 Dashboard running at http://localhost:8080 (Press Control+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard.")
