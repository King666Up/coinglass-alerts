#!/usr/bin/env python3
"""
快速测试脚本，验证项目基本功能
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def quick_test():
    print("🚀 快速测试 CoinGlass 项目...")
    
    # 1. 测试模块导入
    print("\n1. 测试模块导入...")
    try:
        from coinglass_api import CoinGlassAPI
        print("   ✅ CoinGlassAPI 导入成功")
    except Exception as e:
        print(f"   ❌ CoinGlassAPI 导入失败: {e}")
        return False
    
    try:
        from alert_system import AlertSystem
        print("   ✅ AlertSystem 导入成功")
    except Exception as e:
        print(f"   ❌ AlertSystem 导入失败: {e}")
        return False
    
    # 2. 测试API客户端基本功能（不实际调用API）
    print("\n2. 测试API客户端功能...")
    try:
        api_client = CoinGlassAPI()
        print("   ✅ API客户端创建成功")
        
        # 测试一些不涉及网络请求的方法
        symbol = api_client.get_contract_symbol("Binance", "BTC")
        if symbol == "Binance_BTCUSDT":
            print(f"   ✅ 合约符号生成正常: {symbol}")
        else:
            print(f"   ❌ 合约符号生成异常: {symbol}")
            return False
            
        spot_symbol = api_client.get_spot_symbol("Binance", "BTC")
        if spot_symbol == "Binance_SPOT_BTCUSDT":
            print(f"   ✅ 现货符号生成正常: {spot_symbol}")
        else:
            print(f"   ❌ 现货符号生成异常: {spot_symbol}")
            return False
    except Exception as e:
        print(f"   ❌ API客户端测试失败: {e}")
        return False
    
    # 3. 测试告警系统初始化
    print("\n3. 测试告警系统初始化...")
    try:
        import os
        config_path = Path(__file__).parent / "config.example.json"
        if config_path.exists():
            from alert_system import AlertSystem
            alert_system = AlertSystem(str(config_path))
            print("   ✅ 告警系统初始化成功")
        else:
            print("   ⚠️  配置文件不存在，跳过初始化测试")
    except Exception as e:
        print(f"   ❌ 告警系统初始化失败: {e}")
        return False
    
    print("\n✅ 所有快速测试通过！项目已正确安装并可以使用。")
    print("\n💡 提示：")
    print("   - 项目虚拟环境位于: coinglass-alerts/venv/")
    print("   - 运行项目前请先激活虚拟环境: source venv/bin/activate")
    print("   - 然后可以运行: python src/main.py")
    print("   - 要运行测试: python test_project.py")
    
    return True

if __name__ == "__main__":
    success = quick_test()
    if not success:
        print("\n❌ 测试失败！")
        sys.exit(1)
    else:
        print("\n🎉 项目安装和测试成功完成！")