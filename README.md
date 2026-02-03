# CoinGlass 增强版告警系统

基于 CoinGlass API 的加密货币市场监控和告警系统，提供实时数据监控、LLM智能分析、基差套利分析和个性化告警功能。

## 功能特性

- **实时数据监控**：获取加密货币价格、持仓量、资金费率等数据
- **基差分析**：现货与期货价差监控，识别套利机会
- **反转信号检测**：基于OI、CVD、资金费率的反转信号识别
- **LLM智能分析**：集成大语言模型进行高级市场分析
- **多交易所支持**：支持 Binance、OKX、Bybit 等主流交易所
- **个性化告警**：可配置的告警规则和通知方式
- **清算热图**：可视化清算风险区域
- **资金流分析**：监控资金流向和大户动向
- **策略生成**：基于多维数据生成交易策略

## 安装与运行

### 1. 环境准备

项目已使用虚拟环境安装了所有依赖：

```bash
# 激活虚拟环境
cd /home/king/.openclaw/workspace/coinglass-alerts
source venv/bin/activate
```

### 2. 快速运行

使用便捷的启动脚本：

```bash
# 查看帮助
./run_project.sh

# 启动连续监控
./run_project.sh start

# 运行单次检查
./run_project.sh single

# 运行测试
./run_project.sh test
```

### 3. 手动运行

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行增强版主程序
python src/main.py

# 运行单次分析
python src/main.py --single

# 运行连续监控
python src/main.py --continuous --interval 5

# 运行示例
python examples/basic_usage.py
```

## 新增功能模块

### 基差分析
- 现货与期货价差实时监控
- 基差异常检测（翻倍、突破历史均值）
- 跨平台基差对比分析
- 基差套利机会识别

### LLM智能分析
- 多维数据融合分析
- 市场情绪智能判断
- 交易策略自动生成
- 风险评估与管理

### 反转信号检测
- 底部反转信号（Long Squeeze）
- 顶部反转信号（Short Squeeze）
- 清算后反转机会识别
- 多重确认机制

## 项目结构

- `src/` - 源代码
  - `coinglass_api.py` - CoinGlass API 客户端
  - `alert_system.py` - 传统告警系统核心
  - `core/` - 核心分析模块
    - `analyzer.py` - 高级分析引擎
    - `llm_processor.py` - LLM处理器
  - `main.py` - 增强版主程序入口
- `examples/` - 使用示例
- `tests/` - 测试文件
- `docs/` - 文档
- `logs/` - 日志文件
- `venv/` - Python 虚拟环境
- `run_project.sh` - 便捷启动脚本
- `test_project.py` - 项目测试脚本
- `PROJECT_PLAN_UPDATE.md` - 项目更新计划

## 配置

更新后的 `config.json` 文件：

```json
{
  "api": {
    "base_url_capi": "https://capi.coinglass.com",
    "base_url_fapi": "https://fapi.coinglass.com",
    "headers": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
  },
  "analysis": {
    "basis_threshold": 0.02,
    "oi_change_threshold": 0.05,
    "funding_rate_threshold": 0.001,
    "enable_advanced_analysis": true,
    "enable_llm_analysis": true
  },
  "llm": {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "enable_market_analysis": true,
    "enable_trading_recommendation": true,
    "enable_risk_assessment": true
  },
  "alerts": {
    "price_threshold": 0.05,
    "volume_threshold": 1000000,
    "oi_change_threshold": 0.02,
    "funding_rate_threshold": 0.1,
    "enable_basis_alerts": true,
    "enable_reversal_alerts": true
  },
  "strategy": {
    "enable_basis_arbitrage": true,
    "enable_reversal_strategy": true,
    "max_position_size": 0.05,
    "stop_loss_percentage": 0.03
  }
}
```

## 使用方法

```bash
# 单次分析模式
python src/main.py --single

# 连续监控模式
python src/main.py --continuous --interval 5

# 交互式模式
python src/main.py
```

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
- 以及新增的基差分析和LLM智能分析功能

## 许可证

MIT

## 风险声明

本系统仅供分析和研究使用，不构成投资建议。加密货币市场具有高风险，请在投资前充分了解风险并咨询专业顾问。