package com.marketfeed;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class MarketDataOrderProcessor {
    private final Map<String, List<MarketDataMessage>> symbolBuckets = new ConcurrentHashMap<>();

    public void enqueue(MarketDataMessage message) {
        symbolBuckets.computeIfAbsent(message.symbol(), key -> new ArrayList<>())
                .add(message);

        symbolBuckets.get(message.symbol()).sort(Comparator.comparing(MarketDataMessage::timestamp));
    }

    public List<MarketDataMessage> snapshotOrderedBySymbolAndTime() {
        List<MarketDataMessage> ordered = new ArrayList<>();
        symbolBuckets.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(entry -> ordered.addAll(entry.getValue()));
        return ordered;
    }
}
