CREATE TABLE IF NOT EXISTS market_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    price NUMERIC(18, 6) NOT NULL,
    volume BIGINT NOT NULL,
    bid_price NUMERIC(18, 6),
    ask_price NUMERIC(18, 6),
    source VARCHAR(32) DEFAULT 'simulated',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trade_log (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(32) NOT NULL,
    side VARCHAR(8) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    price NUMERIC(18, 6) NOT NULL,
    quantity INTEGER NOT NULL,
    strategy_name VARCHAR(64) DEFAULT 'moving_average_cross',
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_market_data_symbol_ts
    ON market_data(symbol, timestamp);

CREATE INDEX IF NOT EXISTS idx_market_data_timestamp
    ON market_data(timestamp);

CREATE INDEX IF NOT EXISTS idx_trade_log_symbol_ts
    ON trade_log(symbol, timestamp);

COMMENT ON TABLE market_data IS '实时行情和历史行情存储表';
COMMENT ON COLUMN market_data.symbol IS '交易标的代码';
COMMENT ON COLUMN market_data.timestamp IS '行情时间戳';
COMMENT ON COLUMN market_data.price IS '最新成交价';
COMMENT ON COLUMN market_data.volume IS '成交量';
COMMENT ON COLUMN market_data.bid_price IS '买一价';
COMMENT ON COLUMN market_data.ask_price IS '卖一价';
COMMENT ON COLUMN market_data.source IS '行情来源';
