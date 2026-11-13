package com.marketfeed;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class MarketDataRepository {
    private final String url;
    private final String user;
    private final String password;

    public MarketDataRepository(String url, String user, String password) {
        this.url = url;
        this.user = user;
        this.password = password;
    }

    public void save(MarketDataMessage message) throws SQLException {
        String sql = "INSERT INTO market_data (symbol, timestamp, price, volume, bid_price, ask_price, source) VALUES (?, ?, ?, ?, ?, ?, ?)";

        try (Connection connection = DriverManager.getConnection(url, user, password);
             PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setString(1, message.symbol());
            statement.setTimestamp(2, java.sql.Timestamp.from(message.timestamp()));
            statement.setBigDecimal(3, java.math.BigDecimal.valueOf(message.price()));
            statement.setLong(4, message.volume());
            statement.setBigDecimal(5, java.math.BigDecimal.valueOf(message.bidPrice()));
            statement.setBigDecimal(6, java.math.BigDecimal.valueOf(message.askPrice()));
            statement.setString(7, message.source());
            statement.executeUpdate();
        }
    }
}
