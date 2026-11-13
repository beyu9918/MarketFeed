package com.marketfeed;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class MarketDataSimulator {
    private final Random random = new Random(42L);

    public List<MarketDataMessage> generate(String symbol, Instant start, int count, double basePrice) {
        List<MarketDataMessage> messages = new ArrayList<>();
        double price = basePrice;

        for (int i = 0; i < count; i++) {
            price = Math.max(1.0, price + (random.nextDouble() - 0.5) * 3.0);
            long volume = 100 + random.nextInt(5000);
            double bid = price - 0.3;
            double ask = price + 0.3;

            messages.add(new MarketDataMessage(
                    symbol,
                    start.plusSeconds(i * 60L),
                    round2(price),
                    volume,
                    round2(bid),
                    round2(ask),
                    "simulator"
            ));
        }

        return messages;
    }

    private double round2(double value) {
        return Math.round(value * 100.0) / 100.0;
    }
}
