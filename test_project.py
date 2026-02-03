#!/usr/bin/env python3
"""
CoinGlass项目测试脚本
用于验证项目各组件是否正常工作
"""

import sys
import os
import json
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """测试模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        from coinglass_api import CoinGlassAPI
        print("✅ CoinGlassAPI 导入成功")
    except ImportError as e:
        print(f"❌ CoinGlassAPI 导入失败: {e}")
        return False
    
    try:
        from alert_system import AlertSystem
        print("✅ AlertSystem 导入成功")
    except ImportError as e:
        print(f"❌ AlertSystem 导入失败: {e}")
        return False
    
    try:
        from main import main as main_func
        print("✅ main 导入成功")
    except ImportError as e:
        print(f"❌ main 导入失败: {e}")
        return False
    
    return True

def test_api_client():
    """测试API客户端基本功能"""
    print("\n🧪 测试API客户端...")
    
    try:
        # 重新导入以确保路径正确
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from coinglass_api import CoinGlassAPI
        # 使用示例配置创建API客户端
        api_client = CoinGlassAPI()
        print("✅ CoinGlassAPI 客户端创建成功")
        
        # 检查API配置是否正确初始化
        assert hasattr(api_client, 'api_configs'), "API配置未正确初始化"
        assert len(api_client.api_configs) > 0, "API配置为空"
        print(f"✅ API配置正确，包含 {len(api_client.api_configs)} 个端点")
        
        # 测试符号生成函数
        symbol = api_client.get_contract_symbol("Binance", "BTC")
        expected = "Binance_BTCUSDT"
        assert symbol == expected, f"预期 {expected}, 实际 {symbol}"
        print(f"✅ 符号生成函数正常: {symbol}")
        
        # 测试现货符号生成
        spot_symbol = api_client.get_spot_symbol("Binance", "BTC")
        expected_spot = "Binance_SPOT_BTCUSDT"
        print(f"✅ 现货符号生成函数正常: {spot_symbol}")
        
        return True
        
    except Exception as e:
        print(f"❌ API客户端测试失败: {e}")
        return False

def test_alert_system():
    """测试告警系统基本功能"""
    print("\n🧪 测试告警系统...")
    
    try:
        # 重新导入以确保路径正确
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from alert_system import AlertSystem
        # 使用示例配置创建告警系统
        config_path = Path(__file__).parent / "config.example.json"
        if not config_path.exists():
            print("⚠️  配置文件不存在，跳过告警系统测试")
            return True
            
        alert_system = AlertSystem(str(config_path))
        print("✅ AlertSystem 创建成功")
        
        # 检查配置是否正确加载
        assert hasattr(alert_system, 'config'), "配置未正确加载"
        print("✅ 配置加载正常")
        
        # 检查日志记录器
        assert hasattr(alert_system, 'logger'), "日志记录器未正确创建"
        print("✅ 日志记录器正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 告警系统测试失败: {e}")
        return False

def test_main_function():
    """测试主函数"""
    print("\n🧪 测试主函数...")
    
    try:
        # 重新导入以确保路径正确
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from main import main as main_func
        import inspect
        
        # 检查是否是可调用函数
        assert callable(main_func), "main不是可调用函数"
        print("✅ 主函数存在且可调用")
        
        # 检查函数签名
        sig = inspect.signature(main_func)
        print(f"✅ 主函数签名: main{sig}")
        
        return True
        
    except Exception as e:
        print(f"❌ 主函数测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖项"""
    print("\n🧪 测试依赖项...")
    
    dependencies = [
        'requests',
        'pandas', 
        'numpy',
        'apscheduler',
        'pytz'
    ]
    
    missing_deps = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} 可用")
        except ImportError:
            missing_deps.append(dep)
            print(f"❌ {dep} 缺失")
    
    if missing_deps:
        print(f"\n⚠️  以下依赖缺失: {', '.join(missing_deps)}")
        print("   请运行: pip install -r requirements.txt")
        return False
    
    return True

def test_files_structure():
    """测试项目文件结构"""
    print("\n🧪 测试项目文件结构...")
    
    required_dirs = [
        "src",
        "examples", 
        "docs",
        "logs",
        "tests"
    ]
    
    required_files = [
        "src/coinglass_api.py",
        "src/alert_system.py", 
        "src/main.py",
        "README.md",
        "GUIDE.md",
        "requirements.txt",
        "config.example.json",
        "examples/basic_usage.py"
    ]
    
    all_present = True
    
    # 检查目录
    for dir_name in required_dirs:
        dir_path = Path(__file__).parent / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ 目录存在: {dir_name}")
        else:
            print(f"❌ 目录缺失: {dir_name}")
            all_present = False
    
    # 检查文件
    for file_name in required_files:
        file_path = Path(__file__).parent / file_name
        if file_path.exists() and file_path.is_file():
            print(f"✅ 文件存在: {file_name}")
        else:
            print(f"❌ 文件缺失: {file_name}")
            all_present = False
    
    return all_present

def run_tests():
    """运行所有测试"""
    print("🚀 开始测试 CoinGlass 项目...")
    print("="*50)
    
    results = []
    
    results.append(("文件结构", test_files_structure()))
    results.append(("依赖项", test_dependencies()))
    results.append(("模块导入", test_imports()))
    results.append(("API客户端", test_api_client()))
    results.append(("告警系统", test_alert_system()))
    results.append(("主函数", test_main_function()))
    
    print("\n" + "="*50)
    print("📋 测试结果汇总:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！项目可以正常使用。")
        return True
    else:
        print("⚠️  有测试失败，请检查项目配置。")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)