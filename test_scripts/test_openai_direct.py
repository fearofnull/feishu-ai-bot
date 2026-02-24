"""
直接测试 OpenAI API 配置
"""
from feishu_bot.config import BotConfig
from feishu_bot.openai_api_executor import OpenAIAPIExecutor

# 加载配置
config = BotConfig.from_env()

print("\n" + "="*60)
print("OpenAI API 配置测试")
print("="*60 + "\n")

# 检查配置
print(f"OPENAI_API_KEY: {'✅ 已配置' if config.openai_api_key else '❌ 未配置'}")
print(f"OPENAI_BASE_URL: {config.openai_base_url or '(使用默认)'}")
print(f"OPENAI_MODEL: {config.openai_model}")

if not config.openai_api_key:
    print("\n❌ 错误: OPENAI_API_KEY 未配置")
    exit(1)

print("\n" + "-"*60)
print("测试 OpenAI API 调用...")
print("-"*60 + "\n")

try:
    # 创建执行器
    executor = OpenAIAPIExecutor(
        api_key=config.openai_api_key,
        base_url=config.openai_base_url,
        model=config.openai_model,
        timeout=30
    )
    
    # 测试简单问答
    test_message = "你好，请用一句话介绍你自己"
    print(f"发送消息: {test_message}\n")
    
    result = executor.execute(test_message)
    
    if result.success:
        print("✅ 测试成功！\n")
        print(f"回复内容:\n{result.stdout}\n")
    else:
        print("❌ 测试失败！\n")
        print(f"错误信息: {result.error_message}")
        if result.stderr:
            print(f"详细错误: {result.stderr}")
    
except Exception as e:
    print(f"❌ 发生异常: {str(e)}")
    import traceback
    traceback.print_exc()

print("="*60)
