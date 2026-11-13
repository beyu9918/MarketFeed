from dataclasses import dataclass
from typing import List


@dataclass
class Trade:
    symbol: str
    side: str
    price: float
    quantity: int
    strategy_name: str
    timestamp: str


class MovingAverageCrossStrategy:
    def __init__(self, fast_window: int = 5, slow_window: int = 20):
        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_trades(self, dataframe):
        trades: List[Trade] = []
        dataframe = dataframe.sort_values(["symbol", "timestamp"]).copy()

        for symbol, group in dataframe.groupby("symbol"):
            group = group.reset_index(drop=True)
            group["fast_ma"] = group["price"].rolling(self.fast_window, min_periods=1).mean()
            group["slow_ma"] = group["price"].rolling(self.slow_window, min_periods=1).mean()
            prev_position = 0

            for idx, row in group.iterrows():
                if row["fast_ma"] > row["slow_ma"] and prev_position != 1:
                    trades.append(Trade(symbol, "BUY", float(row["price"]), 1, "moving_average_cross", str(row["timestamp"])))
                    prev_position = 1
                elif row["fast_ma"] < row["slow_ma"] and prev_position != 0:
                    trades.append(Trade(symbol, "SELL", float(row["price"]), 1, "moving_average_cross", str(row["timestamp"])))
                    prev_position = 0

        return trades
