"""
测试CLI提供商配置功能

验证DEFAULT_CLI_PROVIDER配置是否正确工作
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from feishu_bot.config import BotConfig
from feishu_bot.smart_router import SmartRouter
from feishu_bot.executor_registry import ExecutorRegistry
from feishu_bot.models import ParsedCommand


def test_cli_provider_config():
    """测试CLI提供商配置"""
    print("\n" + "=" * 60)
    print("测试CLI提供商配置")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {
            "name": "未设置DEFAULT_CLI_PROVIDER",
            "config": {
                "DEFAULT_PROVIDER": "openai",
                "DEFAULT_CLI_PROVIDER": None
            },
            "expected_api_provider": "openai",
            "expected_cli_provider": "openai"  # 应该使用DEFAULT_PROVIDER
        },
        {
            "name": "设置了DEFAULT_CLI_PROVIDER",
            "config": {
                "DEFAULT_PROVIDER": "openai",
                "DEFAULT_CLI_PROVIDER": "gemini"
            },
            "expected_api_provider": "openai",
            "expected_cli_provider": "gemini"  # 应该使用DEFAULT_CLI_PROVIDER
        },
        {
            "name": "DEFAULT_CLI_PROVIDER为空字符串",
            "config": {
                "DEFAULT_PROVIDER": "claude",
                "DEFAULT_CLI_PROVIDER": ""
            },
            "expected_api_provider": "claude",
            "expected_cli_provider": "claude"  # 空字符串应该使用DEFAULT_PROVIDER
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['name']}")
        print("-" * 60)
        
        # 创建模拟的执行器注册表
        registry = ExecutorRegistry()
        
        # 创建路由器
        router = SmartRouter(
            executor_registry=registry,
            default_provider=test_case["config"]["DEFAULT_PROVIDER"],
            default_layer="api",
            default_cli_provider=test_case["config"]["DEFAULT_CLI_PROVIDER"],
            use_ai_intent_classification=False  # 禁用AI分类以便测试
        )
        
        # 验证配置
        print(f"配置:")
        print(f"  DEFAULT_PROVIDER: {test_case['config']['DEFAULT_PROVIDER']}")
        print(f"  DEFAULT_CLI_PROVIDER: {test_case['config']['DEFAULT_CLI_PROVIDER']}")
        print(f"\n路由器状态:")
        print(f"  default_provider: {router.default_provider}")
        print(f"  default_cli_provider: {router.default_cli_provider}")
        
        # 验证API层提供商
        api_provider_match = router.default_provider == test_case["expected_api_provider"]
        print(f"\nAPI层提供商: {router.default_provider}")
        print(f"  预期: {test_case['expected_api_provider']}")
        print(f"  结果: {'通过' if api_provider_match else '失败'}")
        
        # 验证CLI层提供商
        cli_provider_match = router.default_cli_provider == test_case["expected_cli_provider"]
        print(f"\nCLI层提供商: {router.default_cli_provider}")
        print(f"  预期: {test_case['expected_cli_provider']}")
        print(f"  结果: {'通过' if cli_provider_match else '失败'}")
        
        # 总结
        if api_provider_match and cli_provider_match:
            print(f"\n测试用例 {i}: 通过")
        else:
            print(f"\n测试用例 {i}: 失败")
            return False
    
    print("\n" + "=" * 60)
    print("所有测试通过")
    print("=" * 60)
    return True


def test_from_env():
    """测试从.env文件加载配置"""
    print("\n" + "=" * 60)
    print("测试从.env文件加载配置")
    print("=" * 60)
    
    try:
        config = BotConfig.from_env()
        
        print(f"\n加载的配置:")
        print(f"  DEFAULT_PROVIDER: {config.default_provider}")
        print(f"  DEFAULT_LAYER: {config.default_layer}")
        print(f"  DEFAULT_CLI_PROVIDER: {config.default_cli_provider}")
        
        # 验证逻辑
        if config.default_cli_provider:
            print(f"\n当AI判断需要CLI层时:")
            print(f"  将使用提供商: {config.default_cli_provider}")
        else:
            print(f"\n当AI判断需要CLI层时:")
            print(f"  将使用提供商: {config.default_provider} (DEFAULT_PROVIDER)")
        
        print("\n配置加载成功")
        return True
        
    except Exception as e:
        print(f"\n配置加载失败: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CLI提供商配置测试")
    print("=" * 60)
    
    # 运行测试
    test1_passed = test_cli_provider_config()
    test2_passed = test_from_env()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"配置逻辑测试: {'通过' if test1_passed else '失败'}")
    print(f".env加载测试: {'通过' if test2_passed else '失败'}")
    
    if test1_passed and test2_passed:
        print("\n所有测试通过")
        sys.exit(0)
    else:
        print("\n部分测试失败")
        sys.exit(1)
