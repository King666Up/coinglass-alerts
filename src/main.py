#!/usr/bin/env python3
"""
CoinGlass 告警系统 - 主程序
集成基差分析、LLM智能分析和策略生成
"""

import json
import logging
import time
import argparse
from datetime import datetime
from typing import Dict, List
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .core.analyzer import AdvancedAnalyzer, SignalType
from .core.llm_processor import get_llm_processor
from .alert_system import AlertSystem

class EnhancedAlertSystem:
    def __init__(self, config_file: str = "config.json"):
        """
        初始化增强版告警系统
        :param config_file: 配置文件路径
        """
        self.config_file = config_file
        self.load_config()
        self.setup_logging()
        
        # 初始化各个组件
        self.alert_system = AlertSystem(config_file)
        self.analyzer = AdvancedAnalyzer(self.config)
        self.llm_processor = get_llm_processor(self.config)
        
        self.logger.info("增强版告警系统初始化完成")

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.logger.error(f"配置文件 {self.config_file} 不存在")
            raise
        except json.JSONDecodeError:
            self.logger.error(f"配置文件 {self.config_file} 格式错误")
            raise

    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=getattr(logging, self.config.get('logging', {}).get('level', 'INFO')),
            format=self.config.get('logging', {}).get('format', 
                           '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            handlers=[
                logging.FileHandler(self.config.get('logging', {}).get('file', 'logs/main.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('enhanced_alert_system')

    def run_single_analysis_cycle(self):
        """运行单次分析周期"""
        self.logger.info("开始执行单次分析周期...")
        
        try:
            # 1. 运行传统告警系统
            traditional_alerts = self.alert_system.run_single_monitoring_cycle()
            self.logger.info(f"传统告警系统检测到 {len(traditional_alerts)} 个告警")
            
            # 2. 运行高级分析
            analysis_result = self.analyzer.run_analysis_cycle()
            self.logger.info(f"高级分析完成，生成 {analysis_result['signals_count']} 个信号")
            
            # 3. LLM高级分析
            market_data_summary = {
                'data_points': analysis_result['data_points_count'],
                'signals': analysis_result['signals_count'],
                'latest_signals': analysis_result['signals'][:5],  # 只取前5个信号
                'llm_analysis': analysis_result['llm_analysis'],
                'summary': analysis_result['summary']
            }
            
            llm_analysis = self.llm_processor.analyze_market_data(market_data_summary)
            self.logger.info("LLM分析完成")
            
            # 4. 生成交易建议
            trading_recommendation = self.llm_processor.generate_trading_recommendation(llm_analysis)
            self.logger.info("交易建议生成完成")
            
            # 5. 风险评估
            risk_assessment = self.llm_processor.assess_risk(market_data_summary)
            self.logger.info("风险评估完成")
            
            # 6. 组合所有结果
            combined_result = {
                'timestamp': datetime.now().isoformat(),
                'traditional_alerts': traditional_alerts,
                'advanced_signals': analysis_result,
                'llm_analysis': llm_analysis,
                'trading_recommendation': trading_recommendation,
                'risk_assessment': risk_assessment,
                'actionable_insights': self._extract_actionable_insights(
                    analysis_result, trading_recommendation, risk_assessment
                )
            }
            
            # 7. 输出结果
            self._print_results(combined_result)
            
            # 8. 发送通知（如果启用）
            self._send_enhanced_notifications(combined_result)
            
            return combined_result
            
        except Exception as e:
            self.logger.error(f"分析周期执行失败: {e}")
            raise

    def _extract_actionable_insights(self, analysis_result, trading_recommendation, risk_assessment):
        """提取可操作的见解"""
        insights = []
        
        # 从分析结果中提取强信号
        if analysis_result['summary']['strongest_signal']:
            strongest = analysis_result['summary']['strongest_signal']
            insights.append({
                'type': 'strong_signal',
                'content': f"强信号: {strongest['type']} on {strongest['symbol']} (强度: {strongest['strength']:.2f})"
            })
        
        # 从交易建议中提取
        if 'trading_signals' in trading_recommendation:
            insights.append({
                'type': 'trading_recommendation',
                'content': f"交易建议: {trading_recommendation['trading_signals']}"
            })
        
        # 从风险评估中提取
        if 'risk_level' in risk_assessment:
            insights.append({
                'type': 'risk_assessment',
                'content': f"风险等级: {risk_assessment['risk_level']}"
            })
        
        return insights

    def _print_results(self, result):
        """打印结果"""
        print("\n" + "="*80)
        print("💰 COINGLASS 增强分析结果")
        print("="*80)
        
        print(f"\n📅 分析时间: {result['timestamp']}")
        
        # 传统告警
        print(f"\n🔔 传统告警数量: {len(result['traditional_alerts'])}")
        
        # 高级信号
        signals_count = result['advanced_signals']['signals_count']
        print(f"\n📊 高级信号数量: {signals_count}")
        
        if signals_count > 0:
            print("\n🎯 最强信号:")
            strongest = result['advanced_signals']['summary']['strongest_signal']
            if strongest:
                print(f"  • 类型: {strongest['type']}")
                print(f"  • 品种: {strongest['symbol']}")
                print(f"  • 强度: {strongest['strength']:.2f}")
                print(f"  • 描述: {strongest['description']}")
        
        # LLM分析
        print(f"\n🧠 LLM分析:")
        print(f"  • 整体情绪: {result['llm_analysis'].get('market_sentiment', 'N/A')}")
        print(f"  • 风险等级: {result['risk_assessment'].get('risk_level', 'N/A')}")
        
        # 可操作见解
        print(f"\n💡 可操作见解:")
        for i, insight in enumerate(result['actionable_insights'][:5], 1):  # 只显示前5个
            print(f"  {i}. {insight['content']}")
        
        print("="*80)

    def _send_enhanced_notifications(self, result):
        """发送增强通知"""
        # 发送传统告警
        for alert in result['traditional_alerts']:
            self.alert_system.send_notification(alert)
        
        # 发送高级分析结果
        if result['actionable_insights']:
            for insight in result['actionable_insights']:
                enhanced_alert = {
                    'type': f"ENHANCED_{insight['type']}",
                    'symbol': 'SYSTEM',
                    'exchange': 'COINGLASS',
                    'title': f"增强分析: {insight['type']}",
                    'message': insight['content'],
                    'timestamp': result['timestamp']
                }
                self.alert_system.send_notification(enhanced_alert)

    def run_continuous_monitoring(self, interval_minutes: int = 5):
        """运行连续监控"""
        self.logger.info(f"开始连续监控，检查间隔: {interval_minutes} 分钟")
        
        while True:
            try:
                self.run_single_analysis_cycle()
                
                # 等待下一个检查周期
                self.logger.info(f"等待 {interval_minutes} 分钟后进行下次检查...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                self.logger.info("监控已停止")
                break
            except Exception as e:
                self.logger.error(f"监控过程中出现错误: {e}")
                # 等待一段时间后重试
                time.sleep(60)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='CoinGlass 增强版告警系统')
    parser.add_argument('--config', type=str, default='config.json', help='配置文件路径')
    parser.add_argument('--single', action='store_true', help='运行单次分析')
    parser.add_argument('--continuous', action='store_true', help='运行连续监控')
    parser.add_argument('--interval', type=int, default=5, help='监控间隔（分钟）')
    
    args = parser.parse_args()
    
    # 创建日志目录
    os.makedirs('logs', exist_ok=True)
    
    # 初始化系统
    system = EnhancedAlertSystem(args.config)
    
    if args.single:
        # 运行单次分析
        system.run_single_analysis_cycle()
    elif args.continuous:
        # 运行连续监控
        system.run_continuous_monitoring(args.interval)
    else:
        # 交互式选择
        print("请选择运行模式:")
        print("1. 单次分析")
        print("2. 连续监控")
        
        choice = input("请输入选择 (1/2): ").strip()
        
        if choice == '1':
            system.run_single_analysis_cycle()
        elif choice == '2':
            interval = input(f"请输入监控间隔（分钟，默认{args.interval}): ").strip()
            interval = int(interval) if interval.isdigit() else args.interval
            system.run_continuous_monitoring(interval)
        else:
            print("无效选择")

if __name__ == "__main__":
    main()