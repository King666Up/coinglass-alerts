# CoinGlass 加密货币告警系统使用指南

## 项目概述

这是一个基于 CoinGlass API 的加密货币市场监控和告警系统，可以帮助您实时监控加密货币市场的重要变化，包括价格变动、交易量激增、持仓量变化、资金费率异常等。

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd coinglass-alerts
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

复制示例配置文件并根据需要进行修改：

```bash
cp config.example.json config.json
```

编辑 `config.json` 文件，配置以下内容：

- API设置
- 告警阈值
- 监控的币种和交易所
- 通知方式（邮件、Telegram等）

## 配置详解

### API配置

```json
{
  "api": {
    "base_url_capi": "https://capi.coinglass.com",
    "base_url_fapi": "https://fapi.coinglass.com",
    "headers": {
      "User-Agent": "Mozilla/5.0..."
    }
  }
}
```

### 告警配置

```json
{
  "alerts": {
    "price_threshold": 0.05,          // 价格变化阈值（5%）
    "volume_threshold": 1000000,      // 交易量阈值（100万美元）
    "oi_change_threshold": 0.02,      // 持仓量变化阈值（2%）
    "funding_rate_threshold": 0.1,    // 资金费率阈值（10%）
    "enable_price_alerts": true,      // 启用价格告警
    "enable_volume_alerts": true,     // 启用交易量告警
    "enable_oi_alerts": true,         // 启用持仓量告警
    "enable_funding_rate_alerts": true // 启用资金费率告警
  }
}
```

### 监控配置

```json
{
  "monitoring": {
    "symbols": ["BTC", "ETH", "SOL", "XRP", "ADA"],  // 监控的币种
    "exchanges": ["Binance", "OKX", "Bybit", "Coinbase", "Huobi"],  // 监控的交易所
    "interval": "5m",  // 监控间隔
    "lookback_period": 144  // 回顾期
  }
}
```

### 通知配置

```json
{
  "notifications": {
    "telegram": {
      "enabled": false,
      "bot_token": "your-telegram-bot-token",
      "chat_id": "your-chat-id"
    },
    "email": {
      "enabled": false,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your-email@gmail.com",
      "password": "your-app-password",
      "recipients": ["recipient1@example.com", "recipient2@example.com"]
    },
    "console": {
      "enabled": true
    }
  }
}
```

## 使用方法

### 1. 基本使用

运行单次监控检查：

```bash
python src/main.py --single
```

### 2. 连续监控

运行连续监控（默认每5分钟检查一次）：

```bash
python src/main.py
```

指定监控间隔（例如每10分钟）：

```bash
python src/main.py --interval 10
```

### 3. 测试通知

测试通知功能：

```bash
python src/main.py --test-notifications
```

### 4. 使用配置文件

指定配置文件：

```bash
python src/main.py --config /path/to/your/config.json
```

## 示例代码

查看 `examples/` 目录中的示例代码：

```bash
python examples/basic_usage.py
```

## 功能特性

### 实时数据监控

- 价格变化监控
- 交易量激增检测
- 持仓量变化跟踪
- 资金费率异常检测
- 清算水平监控

### 技术分析

- K线数据获取
- 技术指标计算
- 趋势分析

### 告警系统

- 可配置的告警阈值
- 多种通知方式
- 实时告警推送

### 多交易所支持

- Binance
- OKX
- Bybit
- Coinbase
- Huobi
- 更多交易所...

## API支持

系统支持以下CoinGlass API功能：

- K线数据获取
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

## 日志记录

系统会自动记录日志到 `logs/` 目录中，便于调试和监控系统运行状态。

## 常见问题

### 1. API访问限制

如果遇到API访问限制，请适当增加监控间隔时间。

### 2. 通知功能不工作

检查通知配置是否正确，特别是邮箱SMTP设置和Telegram Bot Token。

### 3. 数据解析错误

确保CoinGlass API响应格式没有发生变化，如有变化需要相应调整解析逻辑。

## 开发贡献

欢迎提交Issue和Pull Request来改进项目。

## 许可证

MIT License