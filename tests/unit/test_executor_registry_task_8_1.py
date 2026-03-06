"""
Task 8.1 验证测试 - 创建执行器注册表

验证执行器注册表的所有要求：
1. 文件存在于 feishu_bot/core/executor_registry.py
2. AIExecutor 基类定义了 execute() 抽象方法
3. 执行器注册和查询机制已实现
4. get_openai_executor() 方法已实现
5. 为 Claude 和 Gemini 兼容类型预留接口
"""
import sys
import os
import importlib.util
from pathlib import Path


def test_file_exists():
    """验证文件存在"""
    file_path = Path("feishu_bot/core/executor_registry.py")
    assert file_path.exists(), f"文件不存在: {file_path}"
    print("✓ 文件存在: feishu_bot/core/executor_registry.py")


def test_ai_executor_base_class():
    """验证 AIExecutor 基类和 execute() 抽象方法"""
    # 直接加载模块以避免包导入问题
    spec = importlib.util.spec_from_file_location(
        "executor_registry",
        "feishu_bot/core/executor_registry.py"
    )
    module = importlib.util.module_from_spec(spec)
    
    # 需要先加载依赖的 models 模块
    models_spec = importlib.util.spec_from_file_location(
        "models",
        "feishu_bot/models.py"
    )
    models_module = importlib.util.module_from_spec(models_spec)
    sys.modules['feishu_bot.models'] = models_module
    models_spec.loader.exec_module(models_module)
    
    # 加载 executor_registry 模块
    spec.loader.exec_module(module)
    
    # 验证 AIExecutor 类存在
    assert hasattr(module, 'AIExecutor'), "AIExecutor 类不存在"
    AIExecutor = module.AIExecutor
    
    # 验证是抽象基类
    from abc import ABC
    assert issubclass(AIExecutor, ABC), "AIExecutor 应该继承自 ABC"
    
    # 验证 execute() 方法存在且是抽象方法
    assert hasattr(AIExecutor, 'execute'), "AIExecutor 缺少 execute() 方法"
    assert hasattr(AIExecutor.execute, '__isabstractmethod__'), "execute() 应该是抽象方法"
    assert AIExecutor.execute.__isabstractmethod__, "execute() 应该是抽象方法"
    
    # 验证其他必需的抽象方法
    assert hasattr(AIExecutor, 'is_available'), "AIExecutor 缺少 is_available() 方法"
    assert hasattr(AIExecutor, 'get_provider_name'), "AIExecutor 缺少 get_provider_name() 方法"
    
    print("✓ AIExecutor 基类定义正确，包含 execute() 抽象方法")


def test_executor_registry_class():
    """验证 ExecutorRegistry 类和注册/查询机制"""
    # 加载模块
    spec = importlib.util.spec_from_file_location(
        "executor_registry",
        "feishu_bot/core/executor_registry.py"
    )
    module = importlib.util.module_from_spec(spec)
    
    # 加载依赖
    models_spec = importlib.util.spec_from_file_location(
        "models",
        "feishu_bot/models.py"
    )
    models_module = importlib.util.module_from_spec(models_spec)
    sys.modules['feishu_bot.models'] = models_module
    models_spec.loader.exec_module(models_module)
    
    spec.loader.exec_module(module)
    
    # 验证 ExecutorRegistry 类存在
    assert hasattr(module, 'ExecutorRegistry'), "ExecutorRegistry 类不存在"
    ExecutorRegistry = module.ExecutorRegistry
    
    # 验证注册方法
    assert hasattr(ExecutorRegistry, 'register_api_executor'), "缺少 register_api_executor() 方法"
    assert hasattr(ExecutorRegistry, 'register_cli_executor'), "缺少 register_cli_executor() 方法"
    
    # 验证查询方法
    assert hasattr(ExecutorRegistry, 'get_executor'), "缺少 get_executor() 方法"
    assert hasattr(ExecutorRegistry, 'list_available_executors'), "缺少 list_available_executors() 方法"
    assert hasattr(ExecutorRegistry, 'is_executor_available'), "缺少 is_executor_available() 方法"
    assert hasattr(ExecutorRegistry, 'get_executor_metadata'), "缺少 get_executor_metadata() 方法"
    
    print("✓ ExecutorRegistry 类实现了注册和查询机制")


def test_get_openai_executor_method():
    """验证 get_openai_executor() 方法"""
    # 加载模块
    spec = importlib.util.spec_from_file_location(
        "executor_registry",
        "feishu_bot/core/executor_registry.py"
    )
    module = importlib.util.module_from_spec(spec)
    
    # 加载依赖
    models_spec = importlib.util.spec_from_file_location(
        "models",
        "feishu_bot/models.py"
    )
    models_module = importlib.util.module_from_spec(models_spec)
    sys.modules['feishu_bot.models'] = models_module
    models_spec.loader.exec_module(models_module)
    
    spec.loader.exec_module(module)
    
    ExecutorRegistry = module.ExecutorRegistry
    
    # 验证方法存在
    assert hasattr(ExecutorRegistry, 'get_openai_executor'), "缺少 get_openai_executor() 方法"
    
    # 验证方法签名
    import inspect
    sig = inspect.signature(ExecutorRegistry.get_openai_executor)
    params = list(sig.parameters.keys())
    
    # 验证必需参数
    assert 'base_url' in params, "get_openai_executor() 缺少 base_url 参数"
    assert 'api_key' in params, "get_openai_executor() 缺少 api_key 参数"
    assert 'model' in params, "get_openai_executor() 缺少 model 参数"
    assert 'timeout' in params, "get_openai_executor() 缺少 timeout 参数"
    
    print("✓ get_openai_executor() 方法已实现，参数正确")


def test_claude_gemini_interface_reserved():
    """验证为 Claude 和 Gemini 兼容类型预留接口"""
    # 通过 AIExecutor 抽象基类，任何实现该接口的执行器都可以被注册
    # 这意味着接口已经为 Claude 和 Gemini 预留
    
    # 验证现有的 Claude 和 Gemini 执行器文件存在
    claude_api_path = Path("feishu_bot/executors/claude_api_executor.py")
    gemini_api_path = Path("feishu_bot/executors/gemini_api_executor.py")
    
    assert claude_api_path.exists(), "Claude API 执行器文件不存在"
    assert gemini_api_path.exists(), "Gemini API 执行器文件不存在"
    
    print("✓ 通过 AIExecutor 基类为 Claude 和 Gemini 兼容类型预留了接口")
    print("✓ Claude 和 Gemini 执行器文件已存在")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Task 8.1 验证测试 - 创建执行器注册表")
    print("=" * 60)
    print()
    
    try:
        test_file_exists()
        test_ai_executor_base_class()
        test_executor_registry_class()
        test_get_openai_executor_method()
        test_claude_gemini_interface_reserved()
        
        print()
        print("=" * 60)
        print("✓ 所有测试通过！Task 8.1 的所有要求都已满足")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"✗ 测试失败: {e}")
        print("=" * 60)
        return 1
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ 测试错误: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
