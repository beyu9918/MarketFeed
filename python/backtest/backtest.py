import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psycopg2

from strategy import MovingAverageCrossStrategy


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "DejaVu Sans", "Arial"]
plt.rcParams["axes.unicode_minus"] = False


def load_csv_ticks(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=["symbol", "timestamp", "price", "volume", "bid_price", "ask_price", "source"])

    columns = ["symbol", "timestamp", "price", "volume", "bid_price", "ask_price", "source"]
    df = pd.read_csv(path, header=None, names=columns)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def fetch_market_data() -> pd.DataFrame:
    dsn = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5433")),
        "database": os.getenv("DB_NAME", "marketfeed"),
        "user": os.getenv("DB_USER", "marketfeed"),
        "password": os.getenv("DB_PASSWORD", "marketfeed"),
    }

    try:
        with psycopg2.connect(**dsn) as conn:
            query = """
                SELECT symbol, timestamp, price, volume, bid_price, ask_price
                FROM market_data
                ORDER BY symbol, timestamp
            """
            df = pd.read_sql(query, conn, parse_dates=["timestamp"])
            if not df.empty:
                return df
    except Exception as exc:
        print(f"PostgreSQL unavailable, using CSV fallback data: {exc}")

    csv_path = Path(__file__).resolve().parents[1] / "mock_data" / "sample_ticks.csv"
    df = load_csv_ticks(csv_path)
    if df.empty:
        raise ValueError("No market data available for backtest")
    return df


def generate_simulated_data() -> pd.DataFrame:
    return load_csv_ticks(Path(__file__).resolve().parents[1] / "mock_data" / "sample_ticks.csv")


def compute_strategy_trades(df: pd.DataFrame):
    strategy = MovingAverageCrossStrategy(fast_window=2, slow_window=5)
    return strategy.generate_trades(df)


def compute_signal_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.sort_values(["symbol", "timestamp"]).copy()
    result["ret_1m"] = result.groupby("symbol")["price"].pct_change().fillna(0.0)
    result["fast_ma"] = result.groupby("symbol")["price"].transform(lambda s: s.rolling(2, min_periods=1).mean())
    result["slow_ma"] = result.groupby("symbol")["price"].transform(lambda s: s.rolling(5, min_periods=1).mean())
    result["signal"] = np.where(result["fast_ma"] > result["slow_ma"], 1, 0)
    result["position"] = result.groupby("symbol")["signal"].shift(1).fillna(0)
    result["strategy_return"] = result["ret_1m"] * result["position"]
    return result


def compute_equity_curve(df: pd.DataFrame) -> pd.Series:
    signal_df = compute_signal_features(df)
    symbol_series = []

    for symbol, group in signal_df.groupby("symbol"):
        cumulative = (1 + group["strategy_return"]).cumprod()
        symbol_series.append(pd.Series(cumulative.to_numpy(), index=group.index, name=symbol))

    if not symbol_series:
        return pd.Series([1.0], name="equity")

    portfolio = pd.concat(symbol_series, axis=1).fillna(1.0)
    equity = portfolio.mean(axis=1).rename("equity")
    return equity


def compute_metrics(equity_curve: pd.Series) -> dict:
    if equity_curve.empty:
        return {"total_return": 0.0, "win_rate": 0.0, "max_drawdown": 0.0, "sharpe": 0.0, "sortino": 0.0}

    returns = equity_curve.pct_change().fillna(0.0)
    cumulative = (1 + returns).cumprod()
    total_return = cumulative.iloc[-1] - 1
    win_rate = (returns > 0).mean()
    rolling_peak = cumulative.cummax()
    max_drawdown = ((rolling_peak - cumulative) / rolling_peak).max()
    sharpe = returns.mean() / returns.std(ddof=1) * np.sqrt(252) if returns.std(ddof=1) > 0 else 0.0
    downside = returns[returns < 0]
    sortino = returns.mean() / downside.std(ddof=1) * np.sqrt(252) if len(downside) > 0 and downside.std(ddof=1) > 0 else 0.0

    return {
        "total_return": total_return,
        "win_rate": win_rate,
        "max_drawdown": max_drawdown,
        "sharpe": sharpe,
        "sortino": sortino,
    }


def plot_equity_curve(equity_curve: pd.Series, metrics: dict) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(equity_curve.index, equity_curve.values, color="#2563eb", linewidth=2)
    ax.set_title("MarketFeed Strategy Equity Curve")
    ax.set_xlabel("时间索引")
    ax.set_ylabel("组合净值")
    ax.grid(True, alpha=0.25)

    summary = (
        f"累计收益: {metrics['total_return']:.2%}\n"
        f"胜率: {metrics['win_rate']:.2%}\n"
        f"最大回撤: {metrics['max_drawdown']:.2%}\n"
        f"Sharpe: {metrics['sharpe']:.2f}\n"
        f"Sortino: {metrics['sortino']:.2f}"
    )
    ax.text(0.02, 0.98, summary, transform=ax.transAxes, va="top", bbox=dict(boxstyle="round,pad=0.35", facecolor="white", alpha=0.85))
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "equity_curve.png", dpi=200)
    plt.close(fig)


def export_summary(metrics: dict) -> None:
    summary_path = OUTPUT_DIR / "strategy_summary.txt"
    with summary_path.open("w", encoding="utf-8") as fh:
        for key, value in metrics.items():
            fh.write(f"{key}: {value:.6f}\n")


def export_trade_log(trades) -> None:
    log_path = OUTPUT_DIR / "trade_log.csv"
    pd.DataFrame([
        {
            "symbol": trade.symbol,
            "side": trade.side,
            "price": trade.price,
            "quantity": trade.quantity,
            "strategy_name": trade.strategy_name,
            "timestamp": trade.timestamp,
        }
        for trade in trades
    ]).to_csv(log_path, index=False)


def main() -> None:
    df = fetch_market_data()
    trades = compute_strategy_trades(df)
    export_trade_log(trades)

    equity_curve = compute_equity_curve(df)
    metrics = compute_metrics(equity_curve)
    plot_equity_curve(equity_curve, metrics)
    export_summary(metrics)

    print("Backtest metrics:")
    for key, value in metrics.items():
        print(f"- {key}: {value:.6f}")
    print(f"Trades exported to {OUTPUT_DIR / 'trade_log.csv'}")
    print(f"Chart saved to {OUTPUT_DIR / 'equity_curve.png'}")
    print(f"Summary saved to {OUTPUT_DIR / 'strategy_summary.txt'}")


if __name__ == "__main__":
    main()
