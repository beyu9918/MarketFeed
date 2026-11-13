package com.marketfeed;

import java.time.Instant;

public record MarketDataMessage(
        String symbol,
        Instant timestamp,
        double price,
        long volume,
        double bidPrice,
        double askPrice,
        String source
) {
    public static MarketDataMessage fromCsv(String line) {
        String[] parts = line.split(",");
        if (parts.length < 7) {
            throw new IllegalArgumentException("Invalid CSV market data row: " + line);
        }

        return new MarketDataMessage(
                parts[0].trim(),
                Instant.parse(parts[1].trim()),
                Double.parseDouble(parts[2].trim()),
                Long.parseLong(parts[3].trim()),
                Double.parseDouble(parts[4].trim()),
                Double.parseDouble(parts[5].trim()),
                parts[6].trim()
        );
    }

    public static MarketDataMessage fromJson(String json) {
        String normalized = json.trim();
        if (normalized.startsWith("{")) {
            String symbol = extractJsonValue(normalized, "symbol");
            String timestamp = extractJsonValue(normalized, "timestamp");
            String price = extractJsonValue(normalized, "price");
            String volume = extractJsonValue(normalized, "volume");
            String bid = extractJsonValue(normalized, "bid_price");
            String ask = extractJsonValue(normalized, "ask_price");
            String source = extractJsonValue(normalized, "source");

            return new MarketDataMessage(
                    symbol,
                    Instant.parse(timestamp),
                    Double.parseDouble(price),
                    Long.parseLong(volume),
                    Double.parseDouble(bid),
                    Double.parseDouble(ask),
                    source
            );
        }
        throw new IllegalArgumentException("Unsupported message format: " + json);
    }

    private static String extractJsonValue(String json, String key) {
        String marker = "\"" + key + "\"";
        int keyIndex = json.indexOf(marker);
        if (keyIndex < 0) {
            throw new IllegalArgumentException("Missing field: " + key);
        }
        int valueStart = json.indexOf(':', keyIndex);
        int valueEnd = json.indexOf(',', valueStart);
        if (valueEnd < 0) {
            valueEnd = json.indexOf('}', valueStart);
        }
        String raw = json.substring(valueStart + 1, valueEnd).trim();
        if (raw.startsWith("\"")) {
            return raw.substring(1, raw.length() - 1);
        }
        return raw;
    }
}
