package com.marketfeed;

public class Main {
    public static void main(String[] args) throws Exception {
        String port = System.getenv().getOrDefault("SERVER_PORT", "9001");
        String dbUrl = System.getenv().getOrDefault("DB_URL", "jdbc:postgresql://localhost:5432/marketfeed");
        String dbUser = System.getenv().getOrDefault("DB_USER", "marketfeed");
        String dbPassword = System.getenv().getOrDefault("DB_PASSWORD", "marketfeed");

        MarketDataRepository repository = new MarketDataRepository(dbUrl, dbUser, dbPassword);
        TcpMarketDataServer server = new TcpMarketDataServer(Integer.parseInt(port), repository);

        try {
            server.start();
        } finally {
            server.close();
        }
    }
}
