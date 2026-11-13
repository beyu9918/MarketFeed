package com.marketfeed;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class TcpMarketDataServer implements AutoCloseable {
    private final int port;
    private final MarketDataRepository repository;
    private final MarketDataOrderProcessor processor;
    private final ExecutorService pool;
    private ServerSocket serverSocket;

    public TcpMarketDataServer(int port, MarketDataRepository repository) {
        this.port = port;
        this.repository = repository;
        this.processor = new MarketDataOrderProcessor();
        this.pool = Executors.newFixedThreadPool(8);
    }

    public void start() throws IOException {
        serverSocket = new ServerSocket(port);
        System.out.println("Market data TCP server listening on port " + port + ".");

        while (!serverSocket.isClosed()) {
            Socket clientSocket = serverSocket.accept();
            pool.submit(() -> handleClient(clientSocket));
        }
    }

    private void handleClient(Socket socket) {
        try (socket;
             BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter writer = new PrintWriter(socket.getOutputStream(), true)) {

            String line;
            while ((line = reader.readLine()) != null) {
                try {
                    MarketDataMessage message = MarketDataParser.parse(line);
                    processor.enqueue(message);
                    repository.save(message);
                    System.out.println("Saved: " + message.symbol() + " @ " + message.timestamp() + " | order=" + processor.snapshotOrderedBySymbolAndTime().size());
                    writer.println("OK: " + message.symbol() + " @ " + message.timestamp());
                } catch (Exception ex) {
                    System.err.println("Parse/save error: " + ex.getMessage());
                    writer.println("ERROR: " + ex.getMessage());
                }
            }
        } catch (IOException e) {
            System.err.println("Socket error: " + e.getMessage());
        }
    }

    @Override
    public void close() throws Exception {
        if (serverSocket != null && !serverSocket.isClosed()) {
            serverSocket.close();
        }
        pool.shutdownNow();
    }
}
