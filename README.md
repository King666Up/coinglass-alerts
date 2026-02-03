# CoinGlass 加密货币告警系统

基于 CoinGlass API 的加密货币市场监控和告警系统，提供实时数据监控、技术指标分析和个性化告警功能。

## 功能特性

- **实时数据监控**：获取加密货币价格、持仓量、资金费率等数据
- **技术指标分析**：支持 K 线、RSI、MACD 等技术指标
- **多交易所支持**：支持 Binance、OKX、Bybit 等主流交易所
- **个性化告警**：可配置的告警规则和通知方式
- **清算热图**：可视化清算风险区域
- **资金流分析**：监控资金流向和大户动向

## 安装

```bash
pip install -r requirements.txt
```

## 配置

创建 `config.json` 文件：

```json
{
  "api": {
    "base_url": "https://capi.coinglass.com",
    "headers": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
  },
  "alerts": {
    "price_threshold": 0.05,
    "volume_threshold": 1000000,
    "oi_change_threshold": 0.02,
    "funding_rate_threshold": 0.1
  },
  "notifications": {
    "telegram": {
      "enabled": false,
      "bot_token": "",
      "chat_id": ""
    },
    "email": {
      "enabled": false,
      "smtp_server": "",
      "smtp_port": 587,
      "username": "",
      "password": ""
    }
  }
}
```

## 使用方法

```bash
python src/main.py
```

## 示例

参见 `examples/` 目录下的使用示例。

## API 支持

- K线数据
- 持仓量数据
- 资金费率数据
- 清算数据
- 期权数据
- 期货市场数据
- 现货市场数据
- 指数数据
- 交易所数据
- 交易数据
- 多空数据
- 股票ETF数据
- 灰度数据
- 链上数据
- 首页数据
- Hyperliquid数据
- CME数据
- 经济日历数据
- 市值数据
- 翻转数据
- 其他数据

## 许可证

MIT