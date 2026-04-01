"""GAS Terminal v3 — Module 19: Live Chart Terminal"""
from __future__ import annotations
from gas_terminal.utils import display as D
from gas_terminal import api

MENU = [
    ("1", "📈", "Line Chart"),
    ("2", "🕯 ", "Candlestick Chart"),
    ("3", "📊", "Volume Chart"),
    ("4", "🪙", "Crypto Chart (Binance)"),
    ("5", "🔄", "Auto-refresh Chart"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "📈 Live Chart Terminal")
        if choice == "b":
            break
        elif choice == "1":
            symbol = D.ask("Symbol (e.g. XAUUSD)")
            tf = D.ask("Timeframe (e.g. M15, H1)")
            show_chart(symbol or "XAUUSD", tf or "M15", "line")
        elif choice == "2":
            symbol = D.ask("Symbol")
            tf = D.ask("Timeframe")
            show_chart(symbol or "XAUUSD", tf or "M15", "candle")
        elif choice == "3":
            symbol = D.ask("Symbol")
            tf = D.ask("Timeframe")
            show_chart(symbol or "XAUUSD", tf or "M15", "volume")
        elif choice == "4":
            symbol = D.ask("Binance symbol (e.g. BTCUSDT)")
            _show_binance_chart(symbol or "BTCUSDT")
        elif choice == "5":
            symbol = D.ask("Symbol")
            tf = D.ask("Timeframe")
            interval = D.ask("Refresh interval in seconds (default 30)")
            try:
                interval = int(interval)
            except ValueError:
                interval = 30
            _auto_refresh_chart(symbol or "XAUUSD", tf or "M15", interval)
        D.press_enter()

def show_chart(symbol: str, timeframe: str = "M15", chart_type: str = "line"):
    """Render a chart using plotext in the terminal."""
    D.info(f"Fetching OHLCV data for {symbol} {timeframe}...")
    ohlcv = api.run(api.terminal_ohlcv(symbol, timeframe, limit=100))
    if not ohlcv or not isinstance(ohlcv, list):
        D.error(f"No OHLCV data available for {symbol}.")
        D.info("Chart requires terminal backend to be running.")
        return
    try:
        import plotext as plt
        closes = [candle.get("close", 0) for candle in ohlcv if candle.get("close")]
        highs  = [candle.get("high", 0) for candle in ohlcv if candle.get("high")]
        lows   = [candle.get("low", 0) for candle in ohlcv if candle.get("low")]
        opens  = [candle.get("open", 0) for candle in ohlcv if candle.get("open")]
        times  = list(range(len(closes)))
        plt.clear_figure()
        plt.theme("dark")
        plt.title(f"{symbol} — {timeframe} Chart ({chart_type})")
        if chart_type == "candle" and opens and highs and lows and closes:
            plt.candlestick(times, list(zip(opens, closes, lows, highs)))
        elif chart_type == "volume":
            volumes = [candle.get("volume", 0) for candle in ohlcv if candle.get("volume")]
            plt.bar(times[:len(volumes)], volumes, color="cyan")
            plt.title(f"{symbol} — {timeframe} Volume")
        else:
            plt.plot(times, closes, color="cyan", label="Close")
            if highs:
                plt.plot(times, highs, color="green", label="High")
            if lows:
                plt.plot(times, lows, color="red", label="Low")
        plt.xlabel("Bars")
        plt.ylabel("Price")
        plt.show()
    except ImportError:
        D.error("plotext not installed. Run: pip install plotext")
        _text_chart(ohlcv, symbol, timeframe)
    except Exception as e:
        D.error(f"Chart render error: {e}")
        _text_chart(ohlcv, symbol, timeframe)

def _show_binance_chart(symbol: str):
    D.info(f"Fetching Binance ticker for {symbol}...")
    ticker = api.run(api.binance_ticker(symbol))
    if ticker and "error" not in ticker:
        lines = [f"[bold]{k}:[/bold] {v}" for k, v in ticker.items()]
        D.result_panel(f"Binance — {symbol}", "\n".join(lines), style="yellow")
    else:
        D.error(f"Could not fetch ticker for {symbol}: {ticker.get('error','unknown') if isinstance(ticker,dict) else ticker}")

def _auto_refresh_chart(symbol: str, timeframe: str, interval: int):
    import time
    D.info(f"Auto-refreshing {symbol} {timeframe} every {interval}s. Press Ctrl+C to stop.")
    try:
        while True:
            show_chart(symbol, timeframe, "line")
            D.info(f"Next refresh in {interval}s...")
            time.sleep(interval)
    except KeyboardInterrupt:
        D.info("Auto-refresh stopped.")

def _text_chart(ohlcv: list, symbol: str, timeframe: str):
    """Fallback text-based chart when plotext unavailable."""
    if not ohlcv:
        return
    closes = [c.get("close", 0) for c in ohlcv[-30:] if c.get("close")]
    if not closes:
        return
    min_p = min(closes)
    max_p = max(closes)
    height = 10
    width = len(closes)
    D.console.print(f"\n[bold]{symbol} {timeframe} — Close Price (text chart)[/bold]")
    D.console.print(f"[dim]High: {max_p:.2f}  Low: {min_p:.2f}[/dim]\n")
    chart = []
    for row in range(height, 0, -1):
        threshold = min_p + (max_p - min_p) * row / height
        line = ""
        for price in closes:
            line += "█" if price >= threshold else " "
        chart.append(f"[cyan]{line}[/cyan]")
    for line in chart:
        D.console.print(line)
    D.console.print()
