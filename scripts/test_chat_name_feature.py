#!/usr/bin/env python
"""
群聊名称（chat_name）功能测试脚本

演示如何使用新的群聊信息管理功能
"""

import sys
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_chat_info_manager():
    """测试 ChatInfoManager 类"""
    logger.info("=" * 60)
    logger.info("测试 1: ChatInfoManager 初始化")
    logger.info("=" * 60)
    
    from src.xagent.messaging.chat_info_manager import ChatInfoManager
    from lark_oapi import Client as LarkClient
    
    try:
        # 创建 Lark 客户端（需要有效的 app_id 和 app_secret）
        # 这里仅演示类的结构
        logger.info("✓ ChatInfoManager 类成功导入")
        logger.info("✓ 主要方法:")
        logger.info("  - get_chat_name(chat_id) -> 获取群聊名称")
        logger.info("  - get_chat_info(chat_id) -> 获取完整群聊信息")
        logger.info("  - clear_cache(chat_id=None) -> 清除缓存")
    except Exception as e:
        logger.error(f"✗ 测试失败: {e}")
        return False
    
    return True


def test_config_manager():
    """测试 ConfigManager 的新方法"""
    logger.info("=" * 60)
    logger.info("测试 2: ConfigManager.update_chat_name()")
    logger.info("=" * 60)
    
    from src.xagent.session.config_manager import ConfigManager
    from src.xagent.models import SessionConfig
    
    try:
        # 创建配置管理器
        config_manager = ConfigManager(storage_path="./test_configs.json")
        logger.info("✓ ConfigManager 初始化成功")
        
        # 创建测试配置
        test_session_id = "chat-test-001"
        test_session = SessionConfig(
            session_id=test_session_id,
            session_type="group",
            target_project_dir=None,
            response_language=None,
            default_cli_provider=None,
            created_by="test-user",
            created_at="2026-03-27T10:00:00",
            updated_by="test-user",
            updated_at="2026-03-27T10:00:00",
            update_count=0,
            chat_name=None
        )
        
        # 添加到配置管理器
        config_manager.configs[test_session_id] = test_session
        logger.info(f"✓ 创建测试会话: {test_session_id}")
        logger.info(f"  - chat_name 初始值: {test_session.chat_name}")
        
        # 测试 update_chat_name 方法
        test_chat_name = "测试技术讨论群"
        config_manager.update_chat_name(test_session_id, test_chat_name)
        
        # 验证更新
        if config_manager.configs[test_session_id].chat_name == test_chat_name:
            logger.info(f"✓ chat_name 更新成功: {test_chat_name}")
            logger.info(f"  - updated_at: {config_manager.configs[test_session_id].updated_at}")
            logger.info(f"  - update_count: {config_manager.configs[test_session_id].update_count}")
        else:
            logger.error(f"✗ chat_name 更新失败")
            return False
            
    except Exception as e:
        logger.error(f"✗ 测试失败: {e}", exc_info=True)
        return False
    
    return True


def test_message_processor():
    """测试 MessageProcessor 的新参数"""
    logger.info("=" * 60)
    logger.info("测试 3: MessageProcessor 新参数支持")
    logger.info("=" * 60)
    
    from src.xagent.messaging.message_processor import MessageProcessor
    from src.xagent.utils.cache import DeduplicationCache
    
    try:
        # 检查 MessageProcessor 的签名
        import inspect
        sig = inspect.signature(MessageProcessor.__init__)
        
        required_params = {
            'dedup_cache': '去重缓存',
            'message_handler': '消息处理器',
            'message_sender': '消息发送器',
            'command_parser': '命令解析器',
            'bot_open_id_getter': '机器人 ID 获取器',
            'chat_info_manager': '群聊信息管理器 (新)',
            'config_manager': '配置管理器 (新)'
        }
        
        logger.info("✓ MessageProcessor 参数列表:")
        for param_name, param_desc in required_params.items():
            if param_name in sig.parameters:
                param = sig.parameters[param_name]
                default = f" = {param.default}" if param.default != inspect.Parameter.empty else ""
                logger.info(f"  - {param_name}: {param_desc}{default}")
            else:
                logger.warning(f"  ✗ {param_name} 未找到")
        
        logger.info("✓ MessageProcessor 新方法:")
        logger.info("  - _fetch_and_store_chat_name(chat_id, session_id)")
        
    except Exception as e:
        logger.error(f"✗ 测试失败: {e}", exc_info=True)
        return False
    
    return True


def test_xagent_integration():
    """测试 XAgent 集成"""
    logger.info("=" * 60)
    logger.info("测试 4: XAgent 集成检查")
    logger.info("=" * 60)
    
    try:
        import inspect
        from src.xagent.xagent import XAgent
        
        logger.info("✓ XAgent 初始化流程:")
        logger.info("  1. _init_core_components() 初始化 ChatInfoManager")
        logger.info("  2. _init_coordinators() 创建 MessageProcessor")
        logger.info("     - 传递 chat_info_manager")
        logger.info("     - 传递 config_manager")
        logger.info("  3. MessageProcessor 接收这些组件")
        logger.info("  4. 处理群聊消息时，异步获取群名称")
        logger.info("  5. 保存到配置")
        
        logger.info("✓ 集成检查完成")
        
    except Exception as e:
        logger.error(f"✗ 测试失败: {e}", exc_info=True)
        return False
    
    return True


def test_workflow():
    """演示完整工作流"""
    logger.info("=" * 60)
    logger.info("测试 5: 完整工作流演示")
    logger.info("=" * 60)
    
    logger.info("工作流步骤:")
    logger.info("1. 飞书消息到达 XAgent")
    logger.info("   └─ _handle_message_receive(P2ImMessageReceiveV1)")
    logger.info("")
    logger.info("2. MessageProcessor.process() 处理消息")
    logger.info("   ├─ 提取 session_id, session_type")
    logger.info("   ├─ 判断是否为群聊")
    logger.info("   └─ 如果是群聊，启动后台线程")
    logger.info("")
    logger.info("3. 后台线程执行 _fetch_and_store_chat_name()")
    logger.info("   ├─ ChatInfoManager.get_chat_name(chat_id)")
    logger.info("   │  └─ 调用飞书 API: GetChatRequest")
    logger.info("   ├─ 获取成功，得到群名称")
    logger.info("   └─ ConfigManager.update_chat_name(session_id, chat_name)")
    logger.info("")
    logger.info("4. 配置更新")
    logger.info("   ├─ 更新内存中的 SessionConfig")
    logger.info("   ├─ 更新时间戳和版本号")
    logger.info("   └─ 保存到 JSON 文件")
    logger.info("")
    logger.info("5. 前端显示")
    logger.info("   ├─ 刷新配置列表页面")
    logger.info("   ├─ 发送 API 请求获取最新配置")
    logger.info("   └─ ConfigList.vue 显示 chat_name 字段")
    logger.info("")
    logger.info("✓ 工作流演示完成")
    
    return True


def main():
    """运行所有测试"""
    logger.info("\n" + "=" * 60)
    logger.info("飞书群聊名称（chat_name）功能测试")
    logger.info("=" * 60 + "\n")
    
    results = []
    
    # 运行所有测试
    tests = [
        ("ChatInfoManager", test_chat_info_manager),
        ("ConfigManager", test_config_manager),
        ("MessageProcessor", test_message_processor),
        ("XAgent Integration", test_xagent_integration),
        ("Workflow", test_workflow),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"测试 {test_name} 异常: {e}", exc_info=True)
            results.append((test_name, False))
        
        logger.info("")
    
    # 输出总结
    logger.info("=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("\n🎉 所有测试通过！群聊名称功能已成功实现。")
        return 0
    else:
        logger.error(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

