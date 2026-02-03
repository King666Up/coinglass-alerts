#!/usr/bin/env python3
"""
CoinGlass 加密货币告警系统主程序
"""

import argparse
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from alert_system import AlertSystem


def main():
    parser = argparse.ArgumentParser(description='CoinGlass 加密货币告警系统')
    parser.add_argument('--config', '-c', type=str, default='config.json',
                        help='配置文件路径 (默认: config.json)')
    parser.add_argument('--single', action='store_true',
                        help='只运行一次监控检查，不进入连续模式')
    parser.add_argument('--interval', '-i', type=int, default=5,
                        help='监控检查间隔（分钟，默认: 5分钟）')
    parser.add_argument('--test-notifications', action='store_true',
                        help='测试通知功能')
    
    args = parser.parse_args()
    
    # 检查配置文件是否存在，如果不存在则使用示例配置
    config_path = Path(args.config)
    if not config_path.exists():
        example_config = Path("config.example.json")
        if example_config.exists():
            print(f"警告: 配置文件 {config_path} 不存在，将使用示例配置 {example_config}")
            config_path = example_config
        else:
            print(f"错误: 配置文件 {config_path} 和示例配置都不存在")
            sys.exit(1)
    
    # 创建告警系统实例
    alert_system = AlertSystem(str(config_path))
    
    if args.test_notifications:
        # 测试通知功能
        print("正在测试通知功能...")
        test_alert = {
            'type': 'Test Alert',
            'symbol': 'BTC',
            'exchange': 'Binance',
            'title': '通知功能测试',
            'message': 'CoinGlass告警系统通知功能测试成功！',
            'url': 'https://www.coinglass.com'
        }
        alert_system.send_notification(test_alert)
        print("通知功能测试完成")
        return
    
    if args.single:
        # 运行单次监控检查
        print("运行单次监控检查...")
        alerts = alert_system.run_single_monitoring_cycle()
        if alerts:
            print(f"检测到 {len(alerts)} 个告警:")
            for alert in alerts:
                print(f"- {alert.get('title', 'Alert')}: {alert.get('message', '')}")
        else:
            print("本次检查未检测到告警")
    else:
        # 运行连续监控
        print(f"开始连续监控，检查间隔: {args.interval} 分钟")
        try:
            alert_system.run_continuous_monitoring(args.interval)
        except KeyboardInterrupt:
            print("\n监控已停止")


if __name__ == "__main__":
    main()