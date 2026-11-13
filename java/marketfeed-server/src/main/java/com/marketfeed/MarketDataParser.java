package com.marketfeed;

public final class MarketDataParser {
    private MarketDataParser() {
    }

    public static MarketDataMessage parse(String rawLine) {
        String trimmed = rawLine.trim();
        if (trimmed.isEmpty()) {
            throw new IllegalArgumentException("Empty market data message");
        }

        if (trimmed.startsWith("{")) {
            return MarketDataMessage.fromJson(trimmed);
        }

        if (trimmed.contains(",") && trimmed.split(",").length >= 7) {
            return MarketDataMessage.fromCsv(trimmed);
        }

        throw new IllegalArgumentException("Unsupported market data format: " + trimmed);
    }

    public static String toInsertSql(MarketDataMessage message) {
        return String.format(
                "INSERT INTO market_data (symbol, timestamp, price, volume, bid_price, ask_price, source) VALUES ('%s', TIMESTAMPTZ '%s', %s, %s, %s, %s, '%s')",
                message.symbol(),
                message.timestamp().toString(),
                message.price(),
                message.volume(),
                message.bidPrice(),
                message.askPrice(),
                message.source()
        );
    }
}
