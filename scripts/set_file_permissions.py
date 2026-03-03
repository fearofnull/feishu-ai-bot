#!/usr/bin/env python3
"""
设置配置文件和日志文件的安全权限

此脚本用于在生产环境中设置正确的文件权限以增强安全性：
- 配置文件权限设置为 600（仅所有者可读写）
- 日志文件权限设置为 640（所有者可读写，组可读）

使用方法：
    python scripts/set_file_permissions.py
    
或者使其可执行：
    chmod +x scripts/set_file_permissions.py
    ./scripts/set_file_permissions.py
"""

import os
import sys
import stat
import glob
from pathlib import Path


def set_permissions(file_path: str, mode: int) -> bool:
    """
    设置文件权限
    
    Args:
        file_path: 文件路径
        mode: 权限模式（八进制）
        
    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        if os.path.exists(file_path):
            os.chmod(file_path, mode)
            # 验证权限是否设置成功
            current_mode = stat.S_IMODE(os.stat(file_path).st_mode)
            if current_mode == mode:
                print(f"✓ 已设置 {file_path} 权限为 {oct(mode)}")
                return True
            else:
                print(f"✗ 警告: {file_path} 权限设置可能失败 (期望: {oct(mode)}, 实际: {oct(current_mode)})")
                return False
        else:
            print(f"⊘ 跳过不存在的文件: {file_path}")
            return True
    except PermissionError:
        print(f"✗ 错误: 没有权限修改 {file_path}")
        return False
    except Exception as e:
        print(f"✗ 错误: 设置 {file_path} 权限时出错: {e}")
        return False


def set_config_file_permissions():
    """
    设置配置文件权限为 600（仅所有者可读写）
    
    包括：
    - .env 文件
    - session_configs.json
    - 备份文件
    """
    print("\n=== 设置配置文件权限 (600) ===")
    
    config_files = [
        ".env",
        "data/session_configs.json",
    ]
    
    # 添加所有备份文件
    backup_files = glob.glob("data/session_configs.json.backup*")
    config_files.extend(backup_files)
    
    success_count = 0
    total_count = 0
    
    for file_path in config_files:
        total_count += 1
        if set_permissions(file_path, 0o600):
            success_count += 1
    
    print(f"\n配置文件: {success_count}/{total_count} 成功")
    return success_count == total_count


def set_log_file_permissions():
    """
    设置日志文件权限为 640（所有者可读写，组可读）
    """
    print("\n=== 设置日志文件权限 (640) ===")
    
    # 查找所有日志文件
    log_files = glob.glob("logs/*.log*")
    
    if not log_files:
        print("⊘ 未找到日志文件")
        return True
    
    success_count = 0
    total_count = len(log_files)
    
    for file_path in log_files:
        if set_permissions(file_path, 0o640):
            success_count += 1
    
    print(f"\n日志文件: {success_count}/{total_count} 成功")
    return success_count == total_count


def create_directories_if_needed():
    """
    创建必要的目录（如果不存在）
    """
    directories = ["data", "logs"]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, mode=0o755)
                print(f"✓ 创建目录: {directory}")
            except Exception as e:
                print(f"✗ 错误: 创建目录 {directory} 失败: {e}")


def check_platform():
    """
    检查操作系统平台并给出警告
    """
    if sys.platform == "win32":
        print("⚠ 警告: Windows 系统不完全支持 Unix 风格的文件权限")
        print("   某些权限设置可能不会生效")
        print("   建议在 Linux/Unix 系统上运行此脚本\n")
        return False
    return True


def main():
    """
    主函数
    """
    print("=" * 60)
    print("文件权限设置脚本")
    print("=" * 60)
    
    # 检查平台
    is_unix = check_platform()
    
    # 创建必要的目录
    create_directories_if_needed()
    
    # 设置配置文件权限
    config_success = set_config_file_permissions()
    
    # 设置日志文件权限
    log_success = set_log_file_permissions()
    
    # 总结
    print("\n" + "=" * 60)
    if config_success and log_success:
        print("✓ 所有文件权限设置成功")
        print("=" * 60)
        return 0
    else:
        print("✗ 部分文件权限设置失败")
        print("=" * 60)
        if not is_unix:
            print("\n提示: 在 Windows 上，某些权限设置可能不会生效")
            print("      这是正常的，Windows 使用不同的权限模型")
        return 1


if __name__ == "__main__":
    sys.exit(main())
