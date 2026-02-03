#!/usr/bin/env python3
"""
CoinGlass项目清理脚本
用于完全删除项目及其相关文件
"""

import os
import shutil
import sys
from pathlib import Path

def confirm_cleanup():
    """确认是否执行清理操作"""
    print("⚠️  警告：此操作将永久删除 CoinGlass 项目及其所有相关文件！")
    print("\n将删除的内容包括：")
    print("  - 项目根目录及所有子文件")
    print("  - 日志文件")
    print("  - 配置文件")
    print("  - 生成的所有数据")
    print("\n此操作无法撤销！")
    
    response = input("\n确定要继续吗？输入 'DELETE' 以确认: ")
    if response != 'DELETE':
        print("❌ 清理操作已取消")
        return False
    
    return True

def get_project_files():
    """获取项目中所有文件和目录的列表"""
    project_root = Path(__file__).parent
    files_to_delete = []
    
    # 添加所有项目文件和目录
    for item in project_root.rglob('*'):
        if item.is_file():
            files_to_delete.append(item)
        elif item.is_dir():
            # 检查目录是否为空，如果不是，则也会被删除
            if any(item.iterdir()):  # 非空目录
                files_to_delete.append(item)
    
    # 添加项目根目录本身
    files_to_delete.append(project_root)
    
    # 移除清理脚本本身，以免在执行过程中被删除
    files_to_delete = [f for f in files_to_delete if f != Path(__file__)]
    
    return files_to_delete

def cleanup_project():
    """执行清理操作"""
    project_root = Path(__file__).parent
    
    print(f"🧹 开始清理项目: {project_root}")
    
    # 获取项目中的所有文件
    files_to_delete = []
    
    # 遍历所有项目目录和文件（除了清理脚本本身）
    for item in project_root.rglob('*'):
        if item != Path(__file__):  # 不删除清理脚本本身，直到最后
            files_to_delete.append(item)
    
    # 逆序排序，确保先删除文件，再删除其父目录
    files_to_delete_sorted = sorted(files_to_delete, key=lambda x: str(x), reverse=True)
    
    deleted_count = 0
    error_count = 0
    
    for item in files_to_delete_sorted:
        try:
            if item.is_file():
                item.unlink()
                print(f"🗑️  删除文件: {item}")
            elif item.is_dir():
                item.rmdir()  # 只删除空目录
                print(f"🗑️  删除目录: {item}")
            deleted_count += 1
        except OSError as e:
            # 如果目录非空，使用shutil.rmtree
            try:
                shutil.rmtree(item)
                print(f"🗑️  删除目录(含内容): {item}")
                deleted_count += 1
            except Exception as e2:
                print(f"❌ 删除失败: {item} - {e2}")
                error_count += 1
    
    # 最后删除清理脚本本身
    try:
        Path(__file__).unlink()
        print(f"🗑️  删除清理脚本: {Path(__file__)}")
        deleted_count += 1
    except Exception as e:
        print(f"❌ 删除清理脚本失败: {e}")
        error_count += 1
    
    print(f"\n✅ 清理完成！")
    print(f"🗑️  删除了 {deleted_count} 个项目文件/目录")
    if error_count > 0:
        print(f"⚠️  {error_count} 个文件/目录删除失败")
    
    return True

def cleanup_related_files():
    """清理可能的关联文件"""
    print("\n🧹 清理关联文件...")
    
    related_files = [
        Path.home() / ".openclaw" / "workspace" / "GITHUB_TOKENS.md",  # 全局token记录
        Path("/tmp") / "coinglass_test_*",  # 临时测试文件
    ]
    
    deleted_count = 0
    
    for pattern in related_files:
        if pattern.exists():
            try:
                if pattern.is_file():
                    pattern.unlink()
                    print(f"🗑️  删除关联文件: {pattern}")
                elif pattern.is_dir():
                    shutil.rmtree(pattern)
                    print(f"🗑️  删除关联目录: {pattern}")
                deleted_count += 1
            except Exception as e:
                print(f"⚠️  删除关联文件失败 {pattern}: {e}")
    
    print(f"✅ 清理了 {deleted_count} 个关联文件")
    
def main():
    """主函数"""
    print("🚀 CoinGlass 项目清理工具")
    print("="*50)
    
    if not confirm_cleanup():
        return
    
    success = cleanup_project()
    
    if success:
        # 尝试清理关联文件
        cleanup_related_files()
        print("\n🎉 项目清理完成！")
        print("💡 提示：如果项目目录现在为空，父目录可能也需要清理。")
    else:
        print("\n❌ 项目清理失败！")
        return 1
    
    return 0

def safe_cleanup_with_verification():
    """带验证的安全清理"""
    print("🔍 验证项目路径...")
    
    project_root = Path(__file__).parent
    expected_files = ['README.md', 'requirements.txt', 'src/', 'examples/', 'docs/', 'tests/']
    
    print(f"📁 检查项目根目录: {project_root}")
    
    found_expected = 0
    for expected in expected_files:
        expected_path = project_root / expected.rstrip('/')
        exists = expected_path.exists()
        if expected.endswith('/') and expected_path.is_dir():
            print(f"✅ 找到目录: {expected}")
            found_expected += 1
        elif not expected.endswith('/') and expected_path.is_file():
            print(f"✅ 找到文件: {expected}")
            found_expected += 1
        else:
            print(f"⚠️  未找到: {expected}")
    
    if found_expected < 3:  # 至少找到3个预期文件/目录才认为是正确项目
        print(f"⚠️  项目结构不符合预期，找到 {found_expected}/{len(expected_files)} 个预期项目")
        response = input("是否仍要继续清理？(y/N): ")
        if response.lower() != 'y':
            print("❌ 清理操作已取消")
            return False
    
    print(f"\n✅ 验证通过，找到 {found_expected} 个预期项目文件/目录")
    return True

if __name__ == "__main__":
    # 首先验证项目路径
    if not safe_cleanup_with_verification():
        sys.exit(1)
    
    # 执行清理
    exit_code = main()
    sys.exit(exit_code)