"""
CoinGlass 加密货币告警系统
实现基于 CoinGlass API 的加密货币市场监控和告警功能
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
try:
    from .coinglass_api import CoinGlassAPI
except ImportError:
    # 处理直接运行的情况
    from coinglass_api import CoinGlassAPI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class AlertSystem:
    def __init__(self, config_file: str = "config.json"):
        """
        初始化告警系统
        :param config_file: 配置文件路径
        """
        self.load_config(config_file)
        self.api_client = CoinGlassAPI(self.config)
        self.logger = self.setup_logging()
        
        # 存储上次检查的数据，用于比较
        self.previous_data = {}

    def load_config(self, config_file: str):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，使用默认配置
            with open("config.example.json", 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.logger.warning(f"配置文件 {config_file} 不存在，使用默认配置")
        except json.JSONDecodeError:
            raise ValueError(f"配置文件 {config_file} 格式错误")

    def setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger('coinglass_alerts')
        logger.setLevel(getattr(logging, self.config.get('logging', {}).get('level', 'INFO')))
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            self.config.get('logging', {}).get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 创建文件处理器（如果配置了日志文件）
        log_file = self.config.get('logging', {}).get('file')
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger

    def check_price_changes(self) -> List[Dict[str, Any]]:
        """检查价格变化告警"""
        if not self.config['alerts']['enable_price_alerts']:
            return []
        
        alerts = []
        threshold = self.config['alerts']['price_threshold']
        
        for symbol in self.config['monitoring']['symbols']:
            try:
                # 获取加密货币数据
                data = self.api_client.get_crypto_data(symbol=symbol)
                if data:
                    data_dict = json.loads(data) if isinstance(data, str) else data
                    # 这里需要根据实际API响应结构调整
                    # 假设返回的数据包含价格变化百分比信息
                    # 实际实现需要根据API响应格式进行调整
                    pass
            except Exception as e:
                self.logger.error(f"检查价格变化时出错 {symbol}: {e}")
        
        return alerts

    def check_volume_spikes(self) -> List[Dict[str, Any]]:
        """检查交易量激增告警"""
        if not self.config['alerts']['enable_volume_alerts']:
            return []
        
        alerts = []
        threshold = self.config['alerts']['volume_threshold']
        
        for symbol in self.config['monitoring']['symbols']:
            try:
                # 获取交易量数据
                # 这里需要根据实际API实现
                pass
            except Exception as e:
                self.logger.error(f"检查交易量时出错 {symbol}: {e}")
        
        return alerts

    def check_open_interest_changes(self) -> List[Dict[str, Any]]:
        """检查持仓量变化告警"""
        if not self.config['alerts']['enable_oi_alerts']:
            return []
        
        alerts = []
        threshold = self.config['alerts']['oi_change_threshold']
        
        for symbol in self.config['monitoring']['symbols']:
            try:
                # 获取持仓量数据
                for exchange in self.config['monitoring']['exchanges']:
                    contract_symbol = self.api_client.get_contract_symbol(exchange, symbol)
                    if contract_symbol:
                        oi_data = self.api_client.call_api(
                            "获取持仓量图表_V3", 
                            f"symbol={contract_symbol}&timeType=0&currency=USD&type=0"
                        )
                        
                        if oi_data:
                            oi_dict = json.loads(oi_data) if isinstance(oi_data, str) else oi_data
                            # 分析持仓量变化逻辑
                            # 这里需要根据实际API响应结构调整
                            
            except Exception as e:
                self.logger.error(f"检查持仓量变化时出错 {symbol}: {e}")
        
        return alerts

    def check_funding_rates(self) -> List[Dict[str, Any]]:
        """检查资金费率异常告警"""
        if not self.config['alerts']['enable_funding_rate_alerts']:
            return []
        
        alerts = []
        threshold = self.config['alerts']['funding_rate_threshold']
        
        for symbol in self.config['monitoring']['symbols']:
            try:
                # 获取资金费率数据
                funding_data = self.api_client.call_api("获取资金费率排名")
                if funding_data:
                    funding_dict = json.loads(funding_data) if isinstance(funding_data, str) else funding_data
                    # 检查异常资金费率
                    # 这里需要根据实际API响应结构调整
            except Exception as e:
                self.logger.error(f"检查资金费率时出错 {symbol}: {e}")
        
        return alerts

    def check_liquidation_levels(self) -> List[Dict[str, Any]]:
        """检查清算水平异常"""
        alerts = []
        
        for symbol in self.config['monitoring']['symbols']:
            try:
                for exchange in self.config['monitoring']['exchanges']:
                    contract_symbol = self.api_client.get_contract_symbol(exchange, symbol)
                    if contract_symbol:
                        liq_data = self.api_client.call_api(
                            "获取清算水平_V2",
                            f"symbol={contract_symbol}&limit=100&range=24h"
                        )
                        
                        if liq_data:
                            liq_dict = json.loads(liq_data) if isinstance(liq_data, str) else liq_data
                            # 分析清算数据，检测异常
                            # 这里需要根据实际API响应结构调整
            except Exception as e:
                self.logger.error(f"检查清算水平时出错 {symbol}: {e}")
        
        return alerts

    def generate_kline_signals(self) -> List[Dict[str, Any]]:
        """生成K线技术信号"""
        alerts = []
        
        for symbol in self.config['monitoring']['symbols']:
            try:
                for exchange in self.config['monitoring']['exchanges']:
                    contract_symbol = self.api_client.get_contract_symbol(exchange, symbol)
                    if contract_symbol:
                        # 获取K线数据
                        kline_data = self.api_client.call_api(
                            "获取K线数据_V2",
                            f"symbol={contract_symbol}&interval={self.config['monitoring']['interval']}"
                        )
                        
                        if kline_data:
                            kline_dict = json.loads(kline_data) if isinstance(kline_data, str) else kline_data
                            # 分析K线数据，生成技术信号
                            # 这里需要根据实际API响应结构调整
            except Exception as e:
                self.logger.error(f"生成K线信号时出错 {symbol}: {e}")
        
        return alerts

    def run_single_monitoring_cycle(self) -> List[Dict[str, Any]]:
        """运行单次监控循环，返回所有检测到的告警"""
        self.logger.info("开始执行监控循环...")
        
        all_alerts = []
        
        # 执行各项检查
        all_alerts.extend(self.check_price_changes())
        all_alerts.extend(self.check_volume_spikes())
        all_alerts.extend(self.check_open_interest_changes())
        all_alerts.extend(self.check_funding_rates())
        all_alerts.extend(self.check_liquidation_levels())
        all_alerts.extend(self.generate_kline_signals())
        
        self.logger.info(f"监控循环完成，检测到 {len(all_alerts)} 个告警")
        
        return all_alerts

    def send_notification(self, alert: Dict[str, Any]):
        """发送通知"""
        # 发送控制台通知
        if self.config['notifications']['console']['enabled']:
            self.send_console_notification(alert)
        
        # 发送邮件通知
        email_config = self.config['notifications']['email']
        if email_config['enabled']:
            self.send_email_notification(alert, email_config)
        
        # 发送Telegram通知
        telegram_config = self.config['notifications']['telegram']
        if telegram_config['enabled']:
            self.send_telegram_notification(alert, telegram_config)

    def send_console_notification(self, alert: Dict[str, Any]):
        """发送控制台通知"""
        message = (
            f"🚨 {alert.get('type', 'Alert')} - {alert.get('symbol', 'N/A')} on {alert.get('exchange', 'N/A')}\n"
            f"📈 {alert.get('title', 'Market Alert')}\n"
            f"💬 {alert.get('message', 'No details')}\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🔗 {alert.get('url', 'N/A')}\n"
            f"-" * 50
        )
        print(message)
        self.logger.info(f"Console notification sent: {alert.get('title', 'Alert')}")

    def send_email_notification(self, alert: Dict[str, Any], config: Dict[str, Any]):
        """发送邮件通知"""
        try:
            msg = MIMEMultipart()
            msg['From'] = config['username']
            msg['To'] = ', '.join(config['recipients'])
            msg['Subject'] = f"🚨 CoinGlass 告警: {alert.get('title', 'Market Alert')}"
            
            body = (
                f"告警类型: {alert.get('type', 'N/A')}\n"
                f"交易对: {alert.get('symbol', 'N/A')}\n"
                f"交易所: {alert.get('exchange', 'N/A')}\n"
                f"详情: {alert.get('message', 'No details')}\n"
                f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"链接: {alert.get('url', 'N/A')}\n"
            )
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            
            text = msg.as_string()
            server.sendmail(config['username'], config['recipients'], text)
            server.quit()
            
            self.logger.info(f"Email notification sent: {alert.get('title', 'Alert')}")
        except Exception as e:
            self.logger.error(f"发送邮件通知失败: {e}")

    def send_telegram_notification(self, alert: Dict[str, Any], config: Dict[str, Any]):
        """发送Telegram通知"""
        try:
            import requests
            
            message = (
                f"🚨 *{alert.get('type', 'Alert')}* - "
                f"*{alert.get('symbol', 'N/A')}* on _{alert.get('exchange', 'N/A')}_\n\n"
                f"*{alert.get('title', 'Market Alert')}*\n"
                f"_{alert.get('message', 'No details')}_\n\n"
                f"[查看详情]({alert.get('url', '#')})" if alert.get('url') else ""
            )
            
            url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
            payload = {
                'chat_id': config['chat_id'],
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                self.logger.info(f"Telegram notification sent: {alert.get('title', 'Alert')}")
            else:
                self.logger.error(f"发送Telegram通知失败: {response.text}")
        except Exception as e:
            self.logger.error(f"发送Telegram通知异常: {e}")

    def run_continuous_monitoring(self, interval_minutes: int = 5):
        """运行连续监控"""
        self.logger.info(f"开始连续监控，检查间隔: {interval_minutes} 分钟")
        
        while True:
            try:
                alerts = self.run_single_monitoring_cycle()
                
                # 发送所有检测到的告警
                for alert in alerts:
                    self.send_notification(alert)
                
                # 等待下一个检查周期
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                self.logger.info("监控已停止")
                break
            except Exception as e:
                self.logger.error(f"监控过程中出现错误: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续