"""
飞书 AI 机器人主程序
"""
import os
import sys
import logging
import argparse
import schedule
import time
from threading import Thread

# 配置 SSL 证书
from feishu_bot.ssl_config import configure_ssl
configure_ssl()

# 导入配置和主应用
from feishu_bot.config import BotConfig
from feishu_bot.feishu_bot import FeishuBot

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



def cleanup_expired_sessions(bot: FeishuBot) -> None:
    """清理过期会话的定时任务"""
    try:
        count = bot.session_manager.cleanup_expired_sessions()
        if count > 0:
            logger.info(f"Cleaned up {count} expired sessions")
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")


def run_scheduler(bot: FeishuBot) -> None:
    """运行定时任务调度器"""
    # 每小时清理一次过期会话
    schedule.every().hour.do(cleanup_expired_sessions, bot)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='飞书 AI 机器人')
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别'
    )
    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        # 加载配置
        logger.info("Loading configuration...")
        config = BotConfig.from_env()
        logger.info("✅ Configuration loaded successfully")
        
        # 创建机器人实例
        logger.info("Initializing FeishuBot...")
        bot = FeishuBot(config)
        logger.info("✅ FeishuBot initialized successfully")
        
        # 启动定时任务线程
        scheduler_thread = Thread(target=run_scheduler, args=(bot,), daemon=True)
        scheduler_thread.start()
        logger.info("✅ Scheduler started")
        
        # 启动机器人
        logger.info("Starting FeishuBot...")
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

