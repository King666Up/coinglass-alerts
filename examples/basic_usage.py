"""
CoinGlass 告警系统基本使用示例
"""

import sys
from pathlib import Path
import json

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alert_system import AlertSystem
from coinglass_api import CoinGlassAPI


def example_basic_api_usage():
    """基本API使用示例"""
    print("=== 基本API使用示例 ===")
    
    # 创建API客户端实例
    api_client = CoinGlassAPI()
    
    # 获取比特币数据
    print("\n1. 获取比特币市场数据...")
    btc_data = api_client.get_crypto_data(symbol="BTC", limit=5)
    print(f"BTC数据长度: {len(btc_data) if btc_data else 0} 字符")
    print(f"数据预览: {btc_data[:200] if btc_data else 'No data'}...")
    
    # 获取K线数据
    print("\n2. 获取K线数据...")
    kline_data = api_client.call_api("获取K线数据_V2", "symbol=BTC&interval=1h&limit=10")
    print(f"K线数据长度: {len(kline_data) if kline_data else 0} 字符")
    
    # 获取资金费率
    print("\n3. 获取资金费率...")
    funding_data = api_client.call_api("获取资金费率排名")
    print(f"资金费率数据长度: {len(funding_data) if funding_data else 0} 字符")


def example_alert_system_usage():
    """告警系统使用示例"""
    print("\n=== 告警系统使用示例 ===")
    
    # 创建告警系统实例（使用示例配置）
    try:
        alert_system = AlertSystem("config.example.json")
        
        # 运行单次监控检查
        print("\n运行单次监控检查...")
        alerts = alert_system.run_single_monitoring_cycle()
        
        if alerts:
            print(f"检测到 {len(alerts)} 个告警:")
            for i, alert in enumerate(alerts[:3]):  # 只显示前3个
                print(f"  {i+1}. {alert.get('title', 'Alert')}: {alert.get('message', '')}")
            if len(alerts) > 3:
                print(f"  ... 还有 {len(alerts)-3} 个告警")
        else:
            print("未检测到告警")
            
    except Exception as e:
        print(f"告警系统示例运行出错: {e}")


def example_custom_alert_rules():
    """自定义告警规则示例"""
    print("\n=== 自定义告警规则示例 ===")
    
    # 创建API客户端
    api_client = CoinGlassAPI()
    
    # 获取特定数据进行自定义分析
    print("\n获取ETH持仓量数据...")
    eth_oi_data = api_client.call_api(
        "获取持仓量图表_V3", 
        "symbol=ETH&timeType=0&currency=USD&type=0"
    )
    print(f"ETH持仓量数据长度: {len(eth_oi_data) if eth_oi_data else 0} 字符")
    
    # 获取ETH资金费率
    print("\n获取ETH资金费率...")
    eth_funding_data = api_client.get_history_data_by_interface(
        "Binance_ETHUSDT", "1h", limit=24, 
        interface_name="基础K线"
    )
    print(f"ETH资金费率数据长度: {len(eth_funding_data) if eth_funding_data else 0} 字符")


if __name__ == "__main__":
    print("CoinGlass 告警系统使用示例")
    print("=" * 50)
    
    # 运行各个示例
    example_basic_api_usage()
    example_alert_system_usage()
    example_custom_alert_rules()
    
    print("\n示例运行完成！")