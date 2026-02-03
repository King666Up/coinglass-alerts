"""
CoinGlass API 客户端
提供对 CoinGlass 加密货币数据 API 的访问
"""

import time
import random
import json
import base64
import hashlib
import struct
import urllib.parse
import hmac
import zlib
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CoinGlassAPI:
    def __init__(self, config=None):
        """
        初始化 CoinGlass API 客户端
        :param config: 配置字典，包含API基础URL和请求头
        """
        self.config = config or {}
        self.m_backtest_end_time = 0
        self.m_base_url_capi = self.config.get('api', {}).get('base_url_capi', "https://capi.coinglass.com")
        self.m_base_url_fapi = self.config.get('api', {}).get('base_url_fapi', "https://fapi.coinglass.com")
        self.m_base_url_liquidity = self.config.get('api', {}).get('base_url_liquidity', "https://capi.coinglass.com/liquidity-heatmap")
        
        # 定义基础 URL 类型常量
        self.URL_TYPE_CAPI = 0
        self.URL_TYPE_FAPI = 1
        self.URL_TYPE_LIQUIDITY = 2
        
        # 初始化 API 配置表
        self.api_configs = {}
        self._init_api_configs()
        
        # User-Agent 列表
        self.ua_list = self.config.get('api', {}).get('headers', {}).get('User-Agent', [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ])
        
        # 设置默认请求头
        self.default_headers = self.config.get('api', {}).get('headers', {})

    def _add_config(self, name, path, method, url_type, need_auth, desc):
        """添加API配置"""
        self.api_configs[name] = {
            "name": name,
            "path": path,
            "method": method,
            "url_type": url_type,
            "need_auth": need_auth,
            "desc": desc
        }

    def _init_api_configs(self):
        """初始化所有API端点配置"""
        # K线数据
        self._add_config("获取K线数据_V2", "/api/v2/kline", "GET", 0, False, "获取K线数据（新版）")
        self._add_config("获取K线数据_旧版", "/api/kline", "GET", 0, False, "获取K线数据（旧版）")

        # 持仓量数据
        self._add_config("获取持仓量图表_V3", "/api/openInterest/v3/chart", "GET", 0, False, "获取持仓量图表数据V3")
        self._add_config("获取持仓量变化", "/api/openInterest/change", "GET", 0, False, "获取持仓量变化数据")
        self._add_config("获取持仓量交易量比率", "/api/openInterest/oiVolRadio", "GET", 0, False, "获取持仓量与交易量比率")
        self._add_config("获取交易所持仓量信息", "/api/openInterest/ex/info", "GET", 0, False, "获取交易所持仓量信息")

        # 资金费率数据
        self._add_config("获取资金费率排名", "/api/fundingRate/rank", "GET", 0, False, "获取资金费率排名")
        self._add_config("获取资金费率热图", "/api/fundingRate/heatmap", "GET", 0, False, "获取资金费率热图")
        self._add_config("获取资金费率历史图表_V2", "/api/fundingRate/v2/history/chart", "GET", 0, False, "获取资金费率历史图表V2")
        self._add_config("获取平均资金费率历史图表", "/api/fundingRate/history/avg/chart", "GET", 0, False, "获取平均资金费率历史图表")
        self._add_config("获取资金费率首页_V2", "/api/fundingRate/v2/home", "GET", 0, False, "获取资金费率首页数据V2")
        self._add_config("获取平均资金费率", "/api/fundingRate/avg", "GET", 0, False, "获取平均资金费率")

        # 清算数据
        self._add_config("获取清算水平_V2", "/api/liquidationLevels/v2", "GET", 0, False, "获取清算水平数据V2")
        self._add_config("获取清算热图列表", "/api/liqHeatMap/list", "GET", 0, False, "获取清算热图列表")
        self._add_config("获取清算图表", "/api/futures/liquidation/chart", "GET", 0, False, "获取期货清算图表")
        self._add_config("获取清算订单", "/api/futures/liquidation/order", "GET", 0, False, "获取期货清算订单")
        self._add_config("获取最大清算订单", "/api/futures/liquidation/maxOrder", "GET", 0, False, "获取最大清算订单")
        self._add_config("获取清算热力图计数", "/api/futures/liquidation/count/heatmap", "GET", 0, False, "获取清算热力图计数")
        self._add_config("获取交易所清算信息", "/api/futures/liquidation/ex/info", "GET", 0, False, "获取交易所清算信息")
        self._add_config("获取币种清算热图", "/api/coin/liq/heatmap", "GET", 0, False, "获取币种清算热图")
        self._add_config("获取币种清算数据", "/api/coin/liquidation", "GET", 0, False, "获取币种清算数据")

        # 期权数据
        self._add_config("获取期权图表_V2", "/api/option/v2/chart", "GET", 0, False, "获取期权图表数据V2")
        self._add_config("获取期权持仓量历史", "/api/option/oi/history", "GET", 0, False, "获取期权持仓量历史数据")
        self._add_config("获取期权交易量历史", "/api/option/vol/history", "GET", 0, False, "获取期权交易量历史数据")
        self._add_config("获取期权统计", "/api/option/statistics", "GET", 0, False, "获取期权统计数据")

        # 期货市场数据
        self._add_config("获取期货市场分类", "/api/futures/market/category", "GET", 0, False, "获取期货市场分类数据")
        self._add_config("获取期货大单", "/api/futures/bigOrder", "GET", 0, False, "获取期货大单数据")
        self._add_config("获取期货首页统计", "/api/futures/home/statistics", "GET", 0, False, "获取期货首页统计数据")
        self._add_config("获取期货多空图表", "/api/futures/longShortChart", "GET", 0, False, "获取期货多空图表")
        self._add_config("获取期货多空比率", "/api/futures/longShortRate", "GET", 0, False, "获取期货多空比率")

        # 现货市场数据
        self._add_config("获取现货价格表现", "/api/spot/pricePerformance", "GET", 0, False, "获取现货价格表现数据")
        self._add_config("获取现货价格变化历史", "/api/spot/priceChange/history", "GET", 0, False, "获取现货价格变化历史")
        self._add_config("获取现货币种市场", "/api/spot/coin/markets", "GET", 0, False, "获取现货币种市场数据")
        self._add_config("获取现货支持币种", "/api/spot/support/coin", "GET", 0, False, "获取现货支持币种列表")
        self._add_config("获取现货市值数据", "/api/spot/marketCap/data", "GET", 0, False, "获取现货市值数据")
        self._add_config("获取现货RSI列表", "/api/spot/rsi/list", "GET", 0, False, "获取现货RSI列表")

        # 指数数据
        self._add_config("获取RSI热图", "/api/index/rsiMap", "GET", 0, False, "获取RSI热图数据")
        self._add_config("获取CGDI指数", "/api/index/cgdi", "GET", 0, False, "获取Coinglass CGDI指数")
        self._add_config("获取CGRI指数", "/api/index/cgri", "GET", 0, False, "获取Coinglass CGRI指数")
        self._add_config("获取指数历史", "/api/index/history", "GET", 0, False, "获取指数历史数据")
        self._add_config("获取波动率历史", "/api/index/volatilityHistory", "GET", 0, False, "获取波动率历史数据")

        # 清算热图数据
        self._add_config("获取聚合清算热图", "/api/index/aggregate/liqHeatMap", "GET", 0, False, "获取聚合清算热图")
        self._add_config("获取聚合清算热图_V2", "/api/index/v2/liqHeatMap", "GET", 0, False, "获取聚合清算热图V2")
        self._add_config("获取聚合清算热图_V3", "/api/index/v3/aggregate/liqHeatMap", "GET", 0, False, "获取聚合清算热图V3")
        self._add_config("获取聚合清算热图_V4", "/api/index/v4/aggregate/liqHeatMap", "GET", 0, False, "获取聚合清算热图V4")
        self._add_config("获取聚合清算热图_V5", "/api/index/v5/liqHeatMap", "GET", 0, False, "获取聚合清算热图V5")

        # 交易所数据
        self._add_config("获取交易所全部交易对", "/api/coin/tickers", "GET", 0, False, "获取交易所全部交易对")
        self._add_config("获取交易所链上余额_V3", "/api/exchange/chain/v3/balance", "GET", 0, False, "获取交易所链上余额V3")
        self._add_config("获取交易所资产列表", "/api/exchangeAssets/list", "GET", 0, False, "获取交易所资产列表")

        # 多空数据
        self._add_config("获取多空情绪", "/api/ls/sentiment", "GET", 0, False, "获取多空情绪数据")
        self._add_config("获取多空卡片", "/api/ls/card", "GET", 0, False, "获取多空卡片数据")

    def call_api(self, config_name, query_params=None, timeout=30):
        """
        调用API
        :param config_name: API配置名称
        :param query_params: 查询参数
        :param timeout: 超时时间
        :return: API响应
        """
        # 1. 验证配置名称
        if not config_name:
            return json.dumps({"error": "API配置名称不能为空", "code": "VALIDATION_ERROR"})

        # 2. 验证超时时间
        if timeout < 1 or timeout > 120:
            return json.dumps({"error": "超时时间超出范围 (1-120秒)", "code": "TIMEOUT_RANGE_ERROR", "current": timeout})

        # 3. 验证查询参数格式
        if query_params:
            if "?" in query_params:
                return json.dumps({"error": "查询参数不能包含'?'字符", "code": "QUERY_FORMAT_ERROR"})
            if query_params.startswith("?"):
                return json.dumps({"error": "查询参数不能以'?'开头", "code": "QUERY_FORMAT_ERROR"})

        # 4. 查找配置
        config = self.api_configs.get(config_name)
        if not config:
            available_configs = list(self.api_configs.keys())
            msg = ", ".join(available_configs)
            if len(msg) > 500:
                msg = msg[:500] + f"... (共{len(available_configs)}个配置)"
            return json.dumps({"error": f"API配置未找到: {config_name}", "code": "CONFIG_NOT_FOUND", "available_configs": msg})

        # 5. 构建 URL
        base_url = self.m_base_url_capi
        if config['url_type'] == 1:
            base_url = self.m_base_url_fapi
        elif config['url_type'] == 2:
            base_url = self.m_base_url_liquidity

        full_path = config['path']
        if query_params:
            if "?" in full_path:
                return json.dumps({"error": "API路径已包含查询参数，不能重复添加", "code": "PATH_ERROR"})
            full_path = f"{full_path}?{query_params}"

        return self._send_api_request(base_url, full_path, timeout)

    def set_backtest_mode(self, end_time):
        """设置回测模式"""
        self.m_backtest_end_time = end_time
        return True

    def get_contract_symbol(self, ex_name, symbol):
        """获取合约符号"""
        if ex_name == "Binance":
            return f"{ex_name}_{symbol}USDT"
        if ex_name == "OKX":
            return f"OKX_{symbol}-USDT-SWAP"
        if ex_name == "Gate":
            return f"Gate_{symbol}_USDT"
        if ex_name == "Coinbase":
            return f"Coinbase_{symbol}-PERP"
        if ex_name == "Bybit":
            return f"Bybit_{symbol}USDT"
        if ex_name == "KuCoin":
            return f"KuCoin_{symbol}USDT"
        return ""

    def get_spot_symbol(self, ex_name, symbol):
        """获取现货符号"""
        if ex_name == "Binance":
            return f"{ex_name}_SPOT_{symbol}USDT"
        if ex_name == "OKX":
            return f"OKX_{symbol}-USDT-SWAP"  # 注意：OKX的现货和合约符号可能需要调整
        if ex_name == "Gate":
            return f"Gate_{symbol}_USDT"
        if ex_name == "Coinbase":
            return f"Coinbase_SPOT_{symbol}-USDT"
        if ex_name == "Bybit":
            return f"Bybit_SPOT_{symbol}USDT"
        if ex_name == "KuCoin":
            return f"KuCoin_SPOT_{symbol}USDT"
        return ""

    def get_exchange_tickers(self, ex_name):
        """获取交易所交易对"""
        return self._send_api_request(self.m_base_url_capi, f"/api/coin/tickers?exName={urllib.parse.quote(ex_name)}")

    def get_crypto_data(self, symbol=None, exchange=None, sort_field=None, desc=True, limit=2000):
        """获取加密货币数据"""
        params = ["pageNum=1"]
        if symbol:
            kw = symbol
            if kw.endswith("USDT"):
                kw = kw[:-4]
            params.append(f"keyword={urllib.parse.quote(kw)}")
        if exchange:
            params.append(f"ex={urllib.parse.quote(exchange)}")
        if sort_field:
            params.append(f"sort={sort_field}")
        params.append(f"order={'desc' if desc else 'asc'}")
        params.append(f"pageSize={limit}")
        return self._send_api_request(self.m_base_url_capi, f"/api/home/v2/coinMarkets?{'&'.join(params)}")

    def get_liquidation_heatmap(self, symbol_id, interval, model_version=1):
        """获取清算热图"""
        time_param = self._get_time_interval_param(interval)
        if not time_param:
            return ""
        
        encrypted_data = urllib.parse.quote(self._generate_encrypted_data())
        
        if model_version == 1:
            path = f"/api/index/aggregate/liqHeatMap?merge=true&symbol={symbol_id}{time_param}&data={encrypted_data}"
            return self._send_api_request(self.m_base_url_capi, path)
        elif model_version == 2:
            path = f"/api/index/v3/aggregate/liqHeatMap?merge=true&symbol={symbol_id}{time_param}&data={encrypted_data}"
            return self._send_api_request(self.m_base_url_capi, path)
        elif model_version == 3:
            path = f"/api/index/v4/aggregate/liqHeatMap?merge=true&symbol={symbol_id}&range={interval}&cp=false&data={encrypted_data}"
            return self._send_api_request(self.m_base_url_fapi, path)
        else:
            path = f"/api/index/aggregate/liqHeatMap?merge=true&symbol={symbol_id}{time_param}&data={encrypted_data}"
            return self._send_api_request(self.m_base_url_capi, path)

    def get_history_data_by_interface(self, symbol, interval, limit=None, interface_name="", extra_param=None, end_time=None):
        """通过接口获取历史数据"""
        full_type = ""
        
        # 简单映射
        simple_map = {
            "基础K线": "kline",
            "恐惧贪婪指数": "fear_greed_kline",
            "灰度基金持仓": "grayscale_oi_kline",
            "多空持仓人数比": "global_account_kline",
            "大户账户数多空比": "top_account_kline",
            "大户持仓量多空比": "top_position_kline",
            "币种聚合多空比": "aggregated_ls_kline",
            "鲸鱼指数1": "whale_index_1",
            "鲸鱼指数2": "whale_index_2",
            "鲸鱼指数3": "whale_index_3",
            "鲸鱼指数4": "whale_index_4",
            "预测资金费率": "pfr_kline",
            "平均资金费率K线": "avg_fr_kline",
            "主动买卖量": "buy_sell_qty_kline",
            "主动买卖额": "buy_sell_vol_kline",
            "主动买卖笔数": "buy_sell_number_kline",
            "币种爆仓": "aggregated_liq_kline",
            "交易对爆仓": "liq_kline",
            "币本位聚合爆仓": "aggregated_cm_liq_kline",
            "U本位聚合爆仓": "aggregated_um_liq_kline",
            "净头寸指标": "net_positions",
            "溢价指数": "premium_index",
            "基差": "spread_index",
            "指数价格": "index_price",
            "持仓市值比": "oi_mc_ratio",
            "市值": "cs_market_cap",
            "大户账户数多空比_K线": "top_account_ohlc",
            "大户持仓量多空比_K线": "top_position_ohlc",
            "多空持仓人数比_K线": "global_account_ohlc",
            "聚合合约现货成交量比": "vol_compare",
            "币本位聚合持仓K线": "oi_cm_kline",
            "借贷年化利率": "margin",
            "订单簿压力": "order_book_pressure"
        }

        if interface_name in simple_map:
            full_type = self._combine_full_type(symbol, None, simple_map[interface_name])
        # 复杂逻辑映射
        elif interface_name == "持仓_K线":
            suffix = "coin#oi_kline" if (not extra_param or extra_param == "coin") else "usd#oi_kline"
            full_type = self._combine_full_type(symbol, None, suffix)
        elif interface_name == "币种聚合持仓_K线":
            suffix = "coin#aggregated_oi_kline" if (not extra_param or extra_param == "coin") else "usd#aggregated_oi_kline"
            full_type = self._combine_full_type(symbol, None, suffix)
        elif interface_name == "Coinbase_BTC溢价指数":
            full_type = self._combine_full_type("Binance_BTCUSDT", None, "coinbase_premium_index")
        elif interface_name == "订单薄深度":
            param = extra_param if extra_param else "0.5"
            full_type = self._combine_full_type(symbol, None, f"{param}#hundredth_depth")
        elif interface_name == "聚合合约订单薄深度":
            param = extra_param if extra_param else "0.5"
            prefix = "Binance,Bybit,OKX,Deribit,Bitfinex,dYdX,Bitmex,HTX,Kraken,Crypto.com,Bitunix,Hyperliquid#" + symbol
            full_type = self._combine_full_type(prefix, None, f"{param}#aggregated_contract_hundredth_depth")
        elif interface_name == "聚合现货订单薄深度":
            param = extra_param if extra_param else "0.5"
            prefix = "Binance,OKX,Bybit,Coinbase,Bitfinex,Kraken,Bitstamp,Crypto.com#" + symbol
            full_type = self._combine_full_type(prefix, None, f"{param}#aggregated_spot_hundredth_depth")
        elif interface_name == "聚合合约成交量":
            suffix = "aggregated_buy_sell_coin" if (not extra_param or extra_param == "coin") else "aggregated_buy_sell_usd"
            prefix = "Binance,Bybit,OKX,CME,Deribit,Bitfinex,dYdX,Bitmex,HTX,Kraken,Bitget,CoinEx,Crypto.com,Bitunix,Hyperliquid#" + symbol
            full_type = self._combine_full_type(prefix, None, suffix)
        elif interface_name == "聚合现货成交量":
            suffix = "aggregated_spot_buy_sell_coin" if (not extra_param or extra_param == "coin") else "aggregated_spot_buy_sell_usd"
            prefix = "Binance,OKX,Bybit,Coinbase,Bitfinex,Kraken,Bitstamp,Crypto.com#" + symbol
            full_type = self._combine_full_type(prefix, None, suffix)
        elif interface_name == "CME比特币期货持仓":
            full_type = self._combine_full_type("CME#BTC", None, "oi_um_kline")
        elif interface_name == "CME以太坊期货持仓":
            full_type = self._combine_full_type("CME#ETH", None, "oi_um_kline")
        elif interface_name == "Binance_USDT借贷利率":
            full_type = self._combine_full_type("Binance_USDT", None, "margin")
        elif interface_name == "Bybit_USDT借贷利率":
            full_type = self._combine_full_type("Bybit_USDT", None, "margin")
        elif interface_name == "OKX_USDT借贷利率":
            full_type = self._combine_full_type("OKX_USDT", None, "margin")

        if not full_type:
            return json.dumps({"error": "未找到对应的接口名称"})

        return self._get_history_data(full_type, interval, limit, None, end_time)

    def _combine_full_type(self, symbol, prefix, suffix):
        """组合完整类型"""
        res = ""
        if prefix:
            res += f"{prefix}#"
        res += symbol
        if suffix:
            res += f"#{suffix}"
        return res

    def _get_history_data(self, full_type, interval, limit=1000, start_time=None, end_time=None):
        """获取历史数据"""
        if end_time is None:
            actual_end_time = int(time.time())
            if self.m_backtest_end_time == 0:
                actual_end_time = int(time.time())
            else:
                actual_end_time = self.m_backtest_end_time
        else:
            actual_end_time = end_time

        path = f"/api/v2/kline?symbol={urllib.parse.quote(full_type)}&interval={interval}"
        if start_time:
            path += f"&startTime={start_time}"
        else:
            path += f"&limit={limit if limit else 10}"
        path += f"&endTime={actual_end_time}&minLimit=false"
        return self._send_api_request(self.m_base_url_fapi, path)

    def get_liquidation_max_pain(self, time_range):
        """获取清算最大痛点"""
        return self._send_api_request(self.m_base_url_fapi, f"/api/liqHeatMap/list?range={time_range}")

    def get_large_taker_orders(self, symbol, interval, limit=1000, start_time_str=None, end_time_str=None):
        """获取大额Taker订单"""
        interval_seconds = self._calc_interval_seconds(interval)
        if interval_seconds == 0:
            return ""
        
        now = int(time.time())
        end_time = end_time_str if end_time_str else str(now)
        if not start_time_str:
            start_time = now - (int(limit) * interval_seconds)
        else:
            start_time = start_time_str

        path = f"/api/largeTakerOrder?symbol={urllib.parse.quote(symbol)}&interval={interval}&endTime={end_time}&minLimit=false&limit={limit}&startTime={start_time}"
        return self._send_api_request(self.m_base_url_capi, path)

    # ================= 辅助/底层方法 =================
    def _get_time_interval_param(self, interval):
        """获取时间间隔参数"""
        mapping = {
            "0m": "&interval=5&limit=144", "5m": "&interval=5&limit=288", "15m": "&interval=15&limit=192",
            "30m": "&interval=30&limit=336", "2h": "&interval=h2&limit=372", "0h": "&interval=h6&limit=360",
            "12h": "&interval=h12&limit=336", "1d": "&interval=h24&limit=336", "24h": "&interval=5&limit=288",
            "3d": "&interval=15&limit=288", "7d": "&interval=30&limit=336", "30d": "&interval=h2&limit=372"
        }

        times = ["0m", "5m", "0m", "15m", "0m", "30m", "2h", "0h", "12h", "1d"]
        liq_times = ["12h", "24h", "48h", "3d", "1w", "2w", "1M", "3M", "6M", "1y"]
        results = [
            "&interval=5&limit=144", "&interval=5&limit=288", "&interval=15&limit=192", "&interval=15&limit=288",
            "&interval=30&limit=336", "&interval=30&limit=672", "&interval=h2&limit=372", "&interval=h6&limit=360",
            "&interval=h12&limit=336", "&interval=h24&limit=336"
        ]

        if interval in times:
            return results[times.index(interval)]
        if interval in liq_times:
            return results[liq_times.index(interval)]
        return ""

    def _calc_interval_seconds(self, interval):
        """计算间隔秒数"""
        m = {
            "1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600,
            "4h": 14400, "12h": 43200, "24h": 86400, "1d": 86400
        }
        return m.get(interval, 0)

    def _generate_random_ip(self):
        """生成随机IP"""
        while True:
            ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
            # 避免私有IP段
            if ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172.16."):
                continue
            return ip

    def _generate_api_headers(self):
        """生成API请求头"""
        timestamp = int(time.time() * 1000)
        headers = {
            "CACHE-TS-V2": str(timestamp),
            "USER-AGENT": random.choice(self.ua_list),
            "Accept-Encoding": "gzip"
        }

        ip = self._generate_random_ip()
        ip_headers = [
            "X-FORWARDED-FOR", "X-FORWARDED", "FORWARDED-FOR", "FORWARDED", "X-REQUESTED-WITH",
            "X-FORWARDED-PROTO", "X-FORWARDED-HOST", "X-REMOTE-IP", "X-REMOTE-ADDR", "TRUE-CLIENT-IP",
            "X-CLIENT-IP", "CLIENT-IP", "CLIENT_IP", "X-REAL-IP", "X-REQUEST-IP", "ALI-CDN-REAL-IP",
            "CDN-SRC-IP", "CDN-REAL-IP", "CF-CONNECTING-IP", "X-CLUSTER-CLIENT-IP", "WL-PROXY-CLIENT-IP",
            "PROXY-CLIENT-IP", "FASTLY-CLIENT-IP", "X-ORIGINATING-IP", "X-AZURE-CLIENTIP", "X-GOOGLE-REAL-IP",
            "X-AWS-ELB-CLIENT-IP", "X-EC2-INSTANCE-ID", "X-LB-IP", "X-SERVER-IP", "X-CLOUD-TRACE-CONTEXT",
            "X-APPENGINE-USER-IP", "X-AZURE-REF", "X-AZURE-SOCKETIP", "X-FIREWALL-IP", "X-SECURITY-IP",
            "X-THREAT-IP", "X-BLOCKED-IP", "X-GEOIP-COUNTRY", "X-GEOIP-CITY", "X-GEOIP-REGION",
            "X-CLIENT-GEO-LOCATION", "X-DJANGO-REAL-IP", "X-LARAVEL-REAL-IP", "X-NODE-REAL-IP", "X-PHP-REAL-IP"
        ]

        for h in ip_headers:
            headers[h] = ip

        return headers, str(timestamp)

    def _send_api_request(self, base_url, api_path, timeout=30):
        """发送API请求"""
        full_url = base_url + api_path
        headers, cache_ts_v2 = self._generate_api_headers()
        
        # 合并用户提供的默认请求头
        headers.update(self.default_headers)
        
        try:
            resp = requests.get(full_url, headers=headers, timeout=timeout)
            
            # 处理响应
            if resp.status_code != 200:
                logger.error(f"HTTP请求失败: {full_url}, 状态码: {resp.status_code}")
                return ""
                
            # 获取响应头用于解密
            response_headers = resp.headers
            try:
                json_data = resp.json()
            except ValueError:
                logger.error(f"响应解析失败: {full_url}, 内容: {resp.text[:200]}")
                return ""
                
            code = json_data.get("code")
            if code != "0" and code != 0:
                msg = json_data.get("msg", "")
                if msg:
                    logger.error(f"API错误: code={code}, msg={msg}, URL={full_url}")
                return ""
                
            data_content = json_data.get("data")
            
            # 检查是否需要解密
            if isinstance(data_content, str) and not data_content.strip().startswith("{"):
                return self._decode_coinglass_data(full_url, data_content, response_headers, cache_ts_v2)
                
            # 如果是对象或已经是JSON字符串，转换回字符串返回
            if isinstance(data_content, (dict, list)):
                return json.dumps(data_content)
                
            return str(data_content)
            
        except requests.RequestException as e:
            logger.error(f"请求异常: {e}")
            return ""

    # ================= 加密/解密算法 =================
    def _totp_generate(self, t, secret_key):
        """生成TOTP验证码"""
        # Base32 解码
        key_bytes = self._base32_decode(secret_key)
        if not key_bytes:
            return "000000"
            
        # 时间计数器
        counter = int(t / 30)
        
        # 易语言：到字节集(到长整数(...)) -> 8字节，然后字节集翻转
        # 使用大端序打包，然后反转
        msg = struct.pack('>Q', counter)  # 大端序打包
        msg = msg[::-1]  # 反转字节
        
        # HMAC-SHA1
        hmac_obj = hmac.new(key_bytes, msg, hashlib.sha1)
        digest = hmac_obj.digest()
        
        # 截取
        offset = digest[-1] & 0x0f
        binary = ((digest[offset] & 0x7f) << 24) | \
                 ((digest[offset + 1] & 0xff) << 16) | \
                 ((digest[offset + 2] & 0xff) << 8) | \
                 (digest[offset + 3] & 0xff)
                 
        code = str(binary % 1000000)
        return code.zfill(6)

    def _base32_decode(self, s):
        """简单Base32解码实现"""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
        s = s.replace("=", "")
        data = []
        for char in s:
            idx = alphabet.find(char)
            if idx == -1:
                return b""
            data.append(idx)
            
        # 5 bits per char
        bits = ""
        for val in data:
            bits += format(val, '05b')
            
        bytes_list = []
        for i in range(0, len(bits), 8):
            if i + 8 > len(bits):
                break
            bytes_list.append(int(bits[i:i+8], 2))
            
        return bytes(bytes_list)

    def _generate_encrypted_data(self):
        """生成加密 Data 参数"""
        timestamp = int(time.time())
        
        # 密钥
        key_text = "1f68efd73f8d4921acc0dead41dd39bc"
        key_bytes = key_text.encode('utf-8')
        
        # 生成TOTP
        totp_code = self._totp_generate(timestamp, "I65VU7K5ZQL7WB4E")
        payload = f"{timestamp},{totp_code}"
        
        # AES-256-ECB 加密
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        ct_bytes = cipher.encrypt(pad(payload.encode('utf-8'), AES.block_size))
        return base64.b64encode(ct_bytes).decode('utf-8')

    def _decode_coinglass_data(self, url, data_str, headers, cache_ts_v2):
        """解密响应数据"""
        try:
            v = headers.get("v", "")
            user = headers.get("user", "")
            time_h = headers.get("time", "")
            
            # 提取 api_path
            parsed = urllib.parse.urlparse(url)
            api_path = parsed.path
            
            decryption_key_src = b""
            if v == "0":
                decryption_key_src = self._decrypt_user_header(cache_ts_v2, user)
            elif v == "1":
                decryption_key_src = self._decrypt_user_header(api_path, user)
            elif v == "2":
                decryption_key_src = self._decrypt_user_header(time_h, user)
                
            if not decryption_key_src:
                return data_str
                
            # Gzip 解压 key
            try:
                decryption_key = zlib.decompress(decryption_key_src, 16+zlib.MAX_WBITS)
            except:
                try:
                    decryption_key = zlib.decompress(decryption_key_src)
                except:
                    decryption_key = decryption_key_src  # 可能不需要解压
                    
            # 解密 Data (AES-128-ECB)
            cipher = AES.new(decryption_key, AES.MODE_ECB)
            encrypted_bytes = base64.b64decode(data_str)
            decrypted_bytes = cipher.decrypt(encrypted_bytes)
            
            # 去除 Padding
            try:
                decrypted_bytes = unpad(decrypted_bytes, AES.block_size)
            except:
                pass  # 有时可能不需要unpad或padding方式不同
                
            # Gzip 解压结果
            try:
                final_str = zlib.decompress(decrypted_bytes, 16+zlib.MAX_WBITS).decode('utf-8')
            except:
                try:
                    final_str = zlib.decompress(decrypted_bytes).decode('utf-8')
                except:
                    final_str = decrypted_bytes.decode('utf-8', errors='ignore')
                    
            return final_str
            
        except Exception as e:
            logger.error(f"解密数据失败: {e}")
            return data_str

    def _decrypt_user_header(self, seed, user_header):
        """解密 User Header 获取数据解密密钥"""
        try:
            # n = Base64(seed) -> left 16
            n = base64.b64encode(seed.encode('utf-8'))
            key = n[:16]  # AES-128 Key
            
            cipher = AES.new(key, AES.MODE_ECB)
            encrypted_bytes = base64.b64decode(user_header)
            decrypted = cipher.decrypt(encrypted_bytes)
            
            try:
                decrypted = unpad(decrypted, AES.block_size)
            except:
                pass
                
            return decrypted
            
        except Exception as e:
            logger.error(f"User Header 解密失败: {e}")
            return b""