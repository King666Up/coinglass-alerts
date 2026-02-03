"""
CoinGlass 告警系统 - 智能分析引擎
集成基差分析、LLM分析和策略生成
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd

from ..coinglass_api import CoinGlassAPI

class SignalType(Enum):
    BASIS_ARBITRAGE_LONG = "basis_arbitrage_long"
    BASIS_ARBITRAGE_SHORT = "basis_arbitrage_short"
    REVERSAL_BOTTOM_LONG = "reversal_bottom_long"
    REVERSAL_TOP_SHORT = "reversal_top_short"
    MOMENTUM_LONG = "momentum_long"
    MOMENTUM_SHORT = "momentum_short"
    FUNDING_RATE_LONG = "funding_rate_long"
    FUNDING_RATE_SHORT = "funding_rate_short"
    LIQUIDATION_SQUEEZE_LONG = "liquidation_squeeze_long"
    LIQUIDATION_SQUEEZE_SHORT = "liquidation_squeeze_short"

@dataclass
class MarketSignal:
    """市场信号数据结构"""
    symbol: str
    signal_type: SignalType
    strength: float  # 信号强度 0-1
    confidence: float  # 置信度 0-1
    entry_price: float
    take_profit: float
    stop_loss: float
    timestamp: datetime
    description: str
    additional_info: Dict = None

@dataclass
class MarketDataPoint:
    """市场数据点"""
    symbol: str
    spot_price: float
    futures_price: float
    basis: float
    oi: float
    oi_change: float
    cvd: float
    funding_rate: float
    volume: float
    timestamp: datetime

class AdvancedAnalyzer:
    def __init__(self, config: Dict):
        """
        初始化高级分析器
        :param config: 配置字典
        """
        self.config = config
        self.api_client = CoinGlassAPI(config)
        self.logger = self._setup_logging()
        
        # 分析参数
        self.basis_threshold = config.get('analysis', {}).get('basis_threshold', 0.02)
        self.oi_change_threshold = config.get('analysis', {}).get('oi_change_threshold', 0.05)
        self.funding_rate_threshold = config.get('analysis', {}).get('funding_rate_threshold', 0.001)
        
        # 存储历史数据
        self.data_history: Dict[str, List[MarketDataPoint]] = {}
        self.max_history_length = 1000  # 最大历史数据长度

    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger('advanced_analyzer')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    def collect_market_data(self, symbols: List[str], exchanges: List[str]) -> List[MarketDataPoint]:
        """
        收集市场数据
        """
        data_points = []
        
        for symbol in symbols:
            for exchange in exchanges:
                try:
                    # 获取现货价格
                    spot_symbol = self.api_client.get_spot_symbol(exchange, symbol)
                    if spot_symbol:
                        spot_data = self.api_client.get_crypto_data(symbol=symbol, exchange=exchange)
                        spot_price = self._extract_spot_price(spot_data)
                    else:
                        spot_price = 0.0
                    
                    # 获取期货价格
                    futures_symbol = self.api_client.get_contract_symbol(exchange, symbol)
                    if futures_symbol:
                        futures_data = self.api_client.call_api(
                            "获取K线数据_V2", 
                            f"symbol={futures_symbol}&interval=5m&limit=1"
                        )
                        futures_price = self._extract_futures_price(futures_data)
                    else:
                        futures_price = 0.0
                    
                    # 计算基差
                    basis = self._calculate_basis(spot_price, futures_price) if spot_price > 0 else 0.0
                    
                    # 获取持仓量数据
                    oi_data = self.api_client.call_api(
                        "获取持仓量图表_V3", 
                        f"symbol={futures_symbol}&timeType=0&currency=USD&type=0"
                    )
                    oi, oi_change = self._extract_oi_data(oi_data)
                    
                    # 获取资金费率
                    funding_data = self.api_client.call_api("获取资金费率排名")
                    funding_rate = self._extract_funding_rate(funding_data, symbol)
                    
                    # 获取CVD数据（如果有）
                    cvd = self._get_cvd_data(futures_symbol)
                    
                    # 获取交易量
                    volume = self._extract_volume(futures_data)
                    
                    # 创建数据点
                    data_point = MarketDataPoint(
                        symbol=f"{symbol}_{exchange}",
                        spot_price=spot_price,
                        futures_price=futures_price,
                        basis=basis,
                        oi=oi,
                        oi_change=oi_change,
                        cvd=cvd,
                        funding_rate=funding_rate,
                        volume=volume,
                        timestamp=datetime.now()
                    )
                    
                    data_points.append(data_point)
                    
                    # 存储到历史数据
                    if symbol not in self.data_history:
                        self.data_history[symbol] = []
                    self.data_history[symbol].append(data_point)
                    
                    # 限制历史数据长度
                    if len(self.data_history[symbol]) > self.max_history_length:
                        self.data_history[symbol] = self.data_history[symbol][-self.max_history_length:]
                        
                except Exception as e:
                    self.logger.error(f"收集 {symbol} {exchange} 数据时出错: {e}")
        
        return data_points

    def _extract_spot_price(self, spot_data) -> float:
        """提取现货价格"""
        # 根据实际API响应结构调整
        if spot_data and isinstance(spot_data, dict):
            # 假设现货数据结构中有价格字段
            return spot_data.get('price', 0.0)
        return 0.0

    def _extract_futures_price(self, futures_data) -> float:
        """提取期货价格"""
        # 根据实际API响应结构调整
        if futures_data and isinstance(futures_data, dict):
            # 假设K线数据结构中有收盘价
            klines = futures_data.get('data', [])
            if klines and len(klines) > 0:
                return float(klines[-1][4])  # 假设第5个元素是收盘价
        return 0.0

    def _calculate_basis(self, spot_price: float, futures_price: float) -> float:
        """计算基差"""
        if spot_price == 0:
            return 0.0
        return (futures_price - spot_price) / spot_price

    def _extract_oi_data(self, oi_data) -> Tuple[float, float]:
        """提取持仓量数据"""
        if oi_data and isinstance(oi_data, dict):
            oi_history = oi_data.get('data', {}).get('history', [])
            if len(oi_history) >= 2:
                current_oi = oi_history[-1]['value']
                previous_oi = oi_history[-2]['value']
                oi_change = (current_oi - previous_oi) / previous_oi if previous_oi != 0 else 0.0
                return current_oi, oi_change
            elif len(oi_history) == 1:
                return oi_history[0]['value'], 0.0
        return 0.0, 0.0

    def _extract_funding_rate(self, funding_data, symbol: str) -> float:
        """提取资金费率"""
        if funding_data and isinstance(funding_data, dict):
            rates = funding_data.get('data', [])
            for rate in rates:
                if rate.get('symbol', '').startswith(symbol):
                    return rate.get('fundingRate', 0.0)
        return 0.0

    def _get_cvd_data(self, symbol: str) -> float:
        """获取CVD数据"""
        # 这里需要根据CoinGlass API实际支持的功能来实现
        # 暂时返回0
        return 0.0

    def _extract_volume(self, kline_data) -> float:
        """提取交易量"""
        if kline_data and isinstance(kline_data, dict):
            klines = kline_data.get('data', [])
            if klines and len(klines) > 0:
                return float(klines[-1][5])  # 假设第6个元素是交易量
        return 0.0

    def analyze_market_conditions(self, data_points: List[MarketDataPoint]) -> List[MarketSignal]:
        """
        分析市场条件，生成交易信号
        """
        signals = []
        
        for data_point in data_points:
            # 1. 基差套利信号
            basis_signals = self._analyze_basis_arbitrage(data_point)
            signals.extend(basis_signals)
            
            # 2. 反转信号
            reversal_signals = self._analyze_reversal_signals(data_point)
            signals.extend(reversal_signals)
            
            # 3. 资金费率信号
            funding_signals = self._analyze_funding_rate_signals(data_point)
            signals.extend(funding_signals)
            
            # 4. 动量信号
            momentum_signals = self._analyze_momentum_signals(data_point)
            signals.extend(momentum_signals)
        
        return signals

    def _analyze_basis_arbitrage(self, data: MarketDataPoint) -> List[MarketSignal]:
        """分析基差套利信号"""
        signals = []
        
        # 正基差套利：期货价格过高，做空期货买现货
        if data.basis > self.basis_threshold * 2:
            signal = MarketSignal(
                symbol=data.symbol,
                signal_type=SignalType.BASIS_ARBITRAGE_SHORT,
                strength=min(abs(data.basis) / self.basis_threshold, 1.0),
                confidence=0.7,
                entry_price=data.futures_price,
                take_profit=data.futures_price * (1 - data.basis * 0.5),
                stop_loss=data.futures_price * (1 + abs(data.basis) * 0.1),
                timestamp=data.timestamp,
                description=f"正基差套利机会: 基差 {data.basis:.4f}, 高于阈值 {self.basis_threshold * 2:.4f}"
            )
            signals.append(signal)
        
        # 负基差套利：期货价格过低，做多期货卖现货
        elif data.basis < -self.basis_threshold * 2:
            signal = MarketSignal(
                symbol=data.symbol,
                signal_type=SignalType.BASIS_ARBITRAGE_LONG,
                strength=min(abs(data.basis) / self.basis_threshold, 1.0),
                confidence=0.7,
                entry_price=data.futures_price,
                take_profit=data.futures_price * (1 + abs(data.basis) * 0.5),
                stop_loss=data.futures_price * (1 - abs(data.basis) * 0.1),
                timestamp=data.timestamp,
                description=f"负基差套利机会: 基差 {data.basis:.4f}, 低于阈值 {-self.basis_threshold * 2:.4f}"
            )
            signals.append(signal)
        
        return signals

    def _analyze_reversal_signals(self, data: MarketDataPoint) -> List[MarketSignal]:
        """分析反转信号"""
        signals = []
        
        # 底部反转信号（多头挤压）
        if (data.basis < -self.basis_threshold and  # 负基差
            data.oi_change < -self.oi_change_threshold and  # OI急剧减少
            data.cvd < -1000000):  # 极度负值（大量主动卖单）
            
            signal = MarketSignal(
                symbol=data.symbol,
                signal_type=SignalType.REVERSAL_BOTTOM_LONG,
                strength=min(abs(data.oi_change) / self.oi_change_threshold, 1.0),
                confidence=0.6,
                entry_price=data.futures_price,
                take_profit=data.futures_price * 1.05,
                stop_loss=data.futures_price * 0.98,
                timestamp=data.timestamp,
                description=f"底部反转信号: 基差 {data.basis:.4f}, OI变化 {data.oi_change:.4f}, CVD {data.cvd}"
            )
            signals.append(signal)
        
        # 顶部反转信号（空头挤压）
        elif (data.basis > self.basis_threshold and  # 正基差
              data.oi_change < -self.oi_change_threshold and  # OI急剧减少
              data.cvd > 1000000):  # 极度正值（大量主动买单）
            
            signal = MarketSignal(
                symbol=data.symbol,
                signal_type=SignalType.REVERSAL_TOP_SHORT,
                strength=min(abs(data.oi_change) / self.oi_change_threshold, 1.0),
                confidence=0.6,
                entry_price=data.futures_price,
                take_profit=data.futures_price * 0.95,
                stop_loss=data.futures_price * 1.02,
                timestamp=data.timestamp,
                description=f"顶部反转信号: 基差 {data.basis:.4f}, OI变化 {data.oi_change:.4f}, CVD {data.cvd}"
            )
            signals.append(signal)
        
        return signals

    def _analyze_funding_rate_signals(self, data: MarketDataPoint) -> List[MarketSignal]:
        """分析资金费率信号"""
        signals = []
        
        # 资金费率过高，做空信号
        if data.funding_rate > self.funding_rate_threshold:
            signal = MarketSignal(
                symbol=data.symbol,
                signal_type=SignalType.FUNDING_RATE_SHORT,
                strength=min(data.funding_rate / self.funding_rate_threshold, 1.0),
                confidence=0.5,
                entry_price=data.futures_price,
                take_profit=data.futures_price * 0.98,
                stop_loss=data.futures_price * 1.01,
                timestamp=data.timestamp,
                description=f"高资金费率做空信号: 费率 {data.funding_rate:.6f}, 高于阈值 {self.funding_rate_threshold:.6f}"
            )
            signals.append(signal)
        
        # 负资金费率，做多信号
        elif data.funding_rate < -self.funding_rate_threshold:
            signal = MarketSignal(
                symbol=data.symbol,
                signal_type=SignalType.FUNDING_RATE_LONG,
                strength=min(abs(data.funding_rate) / self.funding_rate_threshold, 1.0),
                confidence=0.5,
                entry_price=data.futures_price,
                take_profit=data.futures_price * 1.02,
                stop_loss=data.futures_price * 0.99,
                timestamp=data.timestamp,
                description=f"负资金费率做多信号: 费率 {data.funding_rate:.6f}, 低于阈值 {-self.funding_rate_threshold:.6f}"
            )
            signals.append(signal)
        
        return signals

    def _analyze_momentum_signals(self, data: MarketDataPoint) -> List[MarketSignal]:
        """分析动量信号"""
        signals = []
        
        # 基于持仓量增加和价格上涨的动量信号
        if (data.oi_change > self.oi_change_threshold and 
            data.volume > self.config.get('analysis', {}).get('volume_threshold', 1000000)):
            
            # 判断价格趋势（这里简化处理，实际应该分析价格序列）
            # 假设价格上涨趋势
            signal = MarketSignal(
                symbol=data.symbol,
                signal_type=SignalType.MOMENTUM_LONG if data.basis > 0 else SignalType.MOMENTUM_SHORT,
                strength=min(data.oi_change / self.oi_change_threshold, 1.0),
                confidence=0.6,
                entry_price=data.futures_price,
                take_profit=data.futures_price * (1.02 if data.basis > 0 else 0.98),
                stop_loss=data.futures_price * (0.99 if data.basis > 0 else 1.01),
                timestamp=data.timestamp,
                description=f"动量信号: OI变化 {data.oi_change:.4f}, 交易量 {data.volume:,.0f}"
            )
            signals.append(signal)
        
        return signals

    def generate_llm_analysis(self, signals: List[MarketSignal], data_points: List[MarketDataPoint]) -> Dict:
        """
        使用LLM生成高级分析
        注意：这里只是模拟LLM分析，实际实现需要集成真实的LLM服务
        """
        # 这里应该是与LLM服务的集成点
        # 模拟LLM分析结果
        llm_analysis = {
            "overall_market_sentiment": "neutral",
            "strongest_signals": [],
            "risk_assessment": "medium",
            "confidence_adjustments": {},
            "additional_insights": []
        }
        
        if signals:
            # 找出最强的信号
            strongest_signals = sorted(signals, key=lambda x: x.strength * x.confidence, reverse=True)[:3]
            llm_analysis["strongest_signals"] = [
                {
                    "symbol": s.symbol,
                    "type": s.signal_type.value,
                    "strength": s.strength,
                    "confidence": s.confidence,
                    "description": s.description
                } for s in strongest_signals
            ]
            
            # 风险评估
            high_confidence_signals = [s for s in signals if s.confidence > 0.7]
            if len(high_confidence_signals) > 3:
                llm_analysis["risk_assessment"] = "high_opportunity"
            elif len([s for s in signals if s.confidence > 0.5]) > 5:
                llm_analysis["risk_assessment"] = "medium_opportunity"
        
        # 模拟一些额外的洞察
        if data_points:
            avg_basis = np.mean([dp.basis for dp in data_points if dp.basis != 0])
            if avg_basis > 0.02:
                llm_analysis["additional_insights"].append("平均基差偏高，期货溢价明显")
            elif avg_basis < -0.02:
                llm_analysis["additional_insights"].append("平均基差偏低，现货溢价明显")
        
        return llm_analysis

    def run_analysis_cycle(self) -> Dict:
        """
        运行一次完整的分析周期
        """
        self.logger.info("开始执行分析周期...")
        
        # 1. 收集市场数据
        symbols = self.config.get('monitoring', {}).get('symbols', ['BTC', 'ETH'])
        exchanges = self.config.get('monitoring', {}).get('exchanges', ['Binance'])
        
        data_points = self.collect_market_data(symbols, exchanges)
        self.logger.info(f"收集到 {len(data_points)} 个数据点")
        
        # 2. 分析市场条件
        signals = self.analyze_market_conditions(data_points)
        self.logger.info(f"生成了 {len(signals)} 个交易信号")
        
        # 3. LLM高级分析
        llm_analysis = self.generate_llm_analysis(signals, data_points)
        
        # 4. 组装结果
        result = {
            "timestamp": datetime.now(),
            "data_points_count": len(data_points),
            "signals_count": len(signals),
            "signals": [
                {
                    "symbol": s.symbol,
                    "type": s.signal_type.value,
                    "strength": s.strength,
                    "confidence": s.confidence,
                    "entry_price": s.entry_price,
                    "take_profit": s.take_profit,
                    "stop_loss": s.stop_loss,
                    "description": s.description
                } for s in signals
            ],
            "llm_analysis": llm_analysis,
            "summary": {
                "strongest_signal": llm_analysis["strongest_signals"][0] if llm_analysis["strongest_signals"] else None,
                "risk_level": llm_analysis["risk_assessment"],
                "total_signals": len(signals)
            }
        }
        
        self.logger.info(f"分析周期完成，风险等级: {llm_analysis['risk_assessment']}")
        
        return result