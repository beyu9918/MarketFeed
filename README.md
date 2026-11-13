# MarketFeed 行情与策略回测系统

这是一个用于个人量化开发练习的项目，覆盖：

- Java TCP 行情接收与解析
- PostgreSQL 交易标的行情存储
- Python 历史行情回测与指标计算
- Docker Compose 本地部署与运行

## 功能升级

本版在原有基础上新增：

- Java 行情处理器，确保按 `symbol + timestamp` 顺序维护数据流
- 模拟行情生产器，用于构造真实 tick/分钟级价格序列
- Python 多指标回测：累计收益、胜率、最大回撤、Sharpe、Sortino
- 自动导出收益曲线图和策略摘要文本

## 目录结构

```text
MarketFeed/
├── README.md
├── docker-compose.yml
├── db/
│   └── init/
│       └── 01_schema.sql
├── java/
│   └── marketfeed-server/
│       ├── Dockerfile
│       ├── pom.xml
│       └── src/main/java/com/marketfeed/
│           ├── Main.java
│           ├── MarketDataMessage.java
│           ├── MarketDataParser.java
│           ├── MarketDataRepository.java
│           ├── MarketDataOrderProcessor.java
│           ├── MarketDataSimulator.java
│           └── TcpMarketDataServer.java
├── python/
│   └── backtest/
│       ├── backtest.py
│       ├── run_backtest.py
│       └── requirements.txt
└── output/
```

## 1. 启动服务

```bash
docker compose up --build
```

启动后：

- PostgreSQL：`localhost:5433`
- Java TCP 服务：`localhost:9002`

## 2. 发送测试行情

```bash
python - <<'PY'
import socket
payload = '{"symbol":"AAPL","timestamp":"2026-11-04T09:30:00Z","price":210.35,"volume":1500,"bid_price":210.20,"ask_price":210.50,"source":"simulated"}'
with socket.create_connection(("localhost", 9002), timeout=5) as sock:
    sock.sendall((payload + "\n").encode())
    print(sock.recv(4096).decode())
PY
```

也支持 CSV 发送：

```text
AAPL,2026-11-04T09:30:00Z,210.35,1500,210.20,210.50,simulated
```

## 3. Python 回测

```bash
cd python/backtest
python -m pip install -r requirements.txt
python run_backtest.py
```

输出文件：

- `python/output/equity_curve.png`
- `python/output/strategy_summary.txt`

## 4. PostgreSQL 数据模型

```sql
CREATE TABLE market_data (
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

CREATE INDEX idx_market_data_symbol_ts
    ON market_data(symbol, timestamp);
```

适合的查询：

```sql
SELECT *
FROM market_data
WHERE symbol = 'AAPL'
  AND timestamp BETWEEN '2026-11-01T00:00:00Z' AND '2026-11-05T23:59:59Z';
```

## 5. 回测指标说明

- 累计收益：策略在回测期内的总收益率
- 胜率：正收益观测占比
- 最大回撤：从峰值到谷底的最大跌幅
- Sharpe：单位风险收益
- Sortino：考虑负波动的风险调整收益

## 6. 设计亮点

- Java 端实时行情接入与按时间顺序处理
- PostgreSQL 联合索引支持标的和时间过滤
- Python 中多策略因子分析和收益曲线可视化
- Docker Compose 提供统一开发环境，便于复现
