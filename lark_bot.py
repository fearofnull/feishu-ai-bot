import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import json
import subprocess
from collections import deque

import os
import certifi

# 使用certifi提供的证书bundle
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['SSL_CERT_DIR'] = ''

# 从配置文件加载配置
from config import FEISHU_APP_ID, FEISHU_APP_SECRET, TARGET_PROJECT_DIR, validate_config

# 验证配置
try:
    validate_config()
    print("✅ 配置加载成功")
except ValueError as e:
    print(f"❌ 配置加载失败: {e}")
    exit(1)

lark.APP_ID = FEISHU_APP_ID
lark.APP_SECRET = FEISHU_APP_SECRET

# 消息ID缓存，用于去重，防止重复回复
# 使用deque确保按照插入顺序移除最早的消息ID
processed_message_ids = deque(maxlen=1000)  # 最大长度1000，自动移除超出的元素

# 指定要让Claude访问的目录
target_dir = TARGET_PROJECT_DIR or r"E:\IdeaProjects\xp-ass-part"

# 注册接收消息事件，处理接收到的消息。
# Register event handler to handle received messages.
# https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/events/receive
def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    # 检查消息是否已处理过，防止重复回复
    message_id = data.event.message.message_id
    if message_id in processed_message_ids:
        print(f"消息已处理过，跳过: {message_id}")
        return

    # 添加到已处理队列
    processed_message_ids.append(message_id)

    # 由于使用了maxlen参数，deque会自动管理大小，超出1000时会移除最早的元素
    res_content = ""
    if data.event.message.message_type == "text":
        res_content = json.loads(data.event.message.content)["text"]
    else:
        res_content = "解析消息失败，请发送文本消息\nparse message failed, please send text message"

    # 检查是否存在parent_id，即是否为引用消息
    quoted_message_content = ""
    if hasattr(data.event.message, 'parent_id') and data.event.message.parent_id:
        try:
            # 调用飞书API获取引用消息的详情
            get_message_request = (
                GetMessageRequest.builder()
                .message_id(data.event.message.parent_id)
                .build()
            )
            get_message_response = client.im.v1.message.get(get_message_request)
            
            if get_message_response.success():
                # 打印响应数据的类型和内容，以便调试
                print(f"响应数据类型：{type(get_message_response.data)}")
                print(f"响应数据：{get_message_response.data}")
                
                # 尝试直接获取消息内容
                try:
                    # 检查响应数据的属性
                    if hasattr(get_message_response.data, 'message'):
                        quoted_message = get_message_response.data.message
                        if hasattr(quoted_message, 'message_type'):
                            if quoted_message.message_type == "text":
                                if hasattr(quoted_message, 'content'):
                                    quoted_message_content = json.loads(quoted_message.content)["text"]
                                    print(f"获取到引用消息内容：{quoted_message_content}")
                                else:
                                    print("引用消息没有content属性")
                            elif quoted_message.message_type == "interactive":
                                if hasattr(quoted_message, 'content'):
                                    quoted_message_content = f"卡片消息：{quoted_message.content}"
                                    print(f"获取到卡片消息内容：{quoted_message_content}")
                                else:
                                    print("引用消息没有content属性")
                            else:
                                quoted_message_content = f"引用消息类型：{quoted_message.message_type}"
                                print(f"引用消息不是文本类型：{quoted_message.message_type}")
                        else:
                            print("引用消息没有message_type属性")
                    else:
                        # 尝试其他可能的属性名
                        print("响应数据没有message属性，尝试其他属性")
                        # 打印所有属性
                        print(f"响应数据的所有属性：{dir(get_message_response.data)}")
                except Exception as e:
                    print(f"解析引用消息时发生错误：{str(e)}")
            else:
                print(f"获取引用消息失败：{get_message_response.msg}")
        except Exception as e:
            print(f"获取引用消息时发生错误：{str(e)}")
    
    # 如果有引用消息，整合消息内容
    if quoted_message_content:
        res_content = f"引用消息：{quoted_message_content}\n\n当前消息：{res_content}"

    # 执行claude命令并捕获输出，将用户输入作为参数传递
    claude_output = ""
    try:
        # 创建临时目录存储Claude配置，解决权限问题
        import tempfile
        import shutil

        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix="claude_")

        # 设置环境变量指向临时目录
        env = os.environ.copy()
        env["CLAUDE_CONFIG_DIR"] = temp_dir

        # 检查目录是否存在
        if os.path.exists(target_dir):
            # 切换到develop分支并拉取最新代码
            try:
                # 切换到develop分支
                git_checkout_result = subprocess.run(
                    ["git", "checkout", "develop"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=target_dir
                )
                
                # 拉取最新代码
                git_pull_result = subprocess.run(
                    ["git", "pull"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=target_dir
                )
                
                # 记录git操作结果
                git_output = f"\nGit操作结果：\n切换分支：{git_checkout_result.stdout}\n{git_checkout_result.stderr}\n拉取代码：{git_pull_result.stdout}\n{git_pull_result.stderr}"
                print(git_output)
            except Exception as git_e:
                git_output = f"\nGit操作失败：{str(git_e)}"
                print(git_output)
            
            # 检查Claude是否可用
            try:
                # 在Windows系统中，使用claude.cmd而不是claude
                # 指定encoding='utf-8'避免UnicodeDecodeError
                # 使用stdin传递prompt，而不是-p参数
                prompt_text = f"请基于目录 {target_dir} 回答问题：{res_content}"
                result = subprocess.run(
                    ["claude.cmd", "--add-dir", target_dir],
                    input=prompt_text,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',  # 指定编码为utf-8
                    timeout=600,  # 增加超时时间到600秒
                    cwd=target_dir  # 切换工作目录到目标项目
                )
                claude_output = f"\nClaude命令输出：\n{result.stdout}"
                if result.stderr:
                    claude_output += f"\n错误信息：\n{result.stderr}"
            except FileNotFoundError:
                claude_output = f"\n执行Claude命令失败：系统找不到Claude命令。请确保Claude命令行工具已安装并添加到系统PATH环境变量中。"
            except Exception as claude_e:
                claude_output = f"\n执行Claude命令失败：{str(claude_e)}"
        else:
            # 目录不存在，直接返回目录不存在的消息
            claude_output = f"\n目录不存在：{target_dir}"
            
        # 清理临时目录
        shutil.rmtree(temp_dir)
    except Exception as e:
        claude_output = f"\n执行Claude命令失败：{str(e)}"
        # 尝试清理临时目录
        try:
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir)
        except:
            pass

    content = json.dumps(
        {
            "text": "收到你发送的消息："
            + res_content
            + "\nReceived message:"
            + res_content
            + claude_output
        }
    )

    if data.event.message.chat_type == "p2p":
        request = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(data.event.message.chat_id)
                .msg_type("text")
                .content(content)
                .build()
            )
            .build()
        )
        # 使用OpenAPI发送消息
        # Use send OpenAPI to send messages
        # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
        response = client.im.v1.message.create(request)

        if not response.success():
            raise Exception(
                f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            )
    else:
        request: ReplyMessageRequest = (
            ReplyMessageRequest.builder()
            .message_id(data.event.message.message_id)
            .request_body(
                ReplyMessageRequestBody.builder()
                .content(content)
                .msg_type("text")
                .build()
            )
            .build()
        )
        # 使用OpenAPI回复消息
        # Reply to messages using send OpenAPI
        # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/reply
        response: ReplyMessageResponse = client.im.v1.message.reply(request)
        if not response.success():
            raise Exception(
                f"client.im.v1.message.reply failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            )


# 注册事件回调
# Register event handler.
event_handler = (
    lark.EventDispatcherHandler.builder("", "")
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1)
    .build()
)


# 创建 LarkClient 对象，用于请求OpenAPI, 并创建 LarkWSClient 对象，用于使用长连接接收事件。
# Create LarkClient object for requesting OpenAPI, and create LarkWSClient object for receiving events using long connection.
client = lark.Client.builder().app_id(lark.APP_ID).app_secret(lark.APP_SECRET).build()
wsClient = lark.ws.Client(
    lark.APP_ID,
    lark.APP_SECRET,
    event_handler=event_handler,
    log_level=lark.LogLevel.DEBUG,
)


def main():
    #  启动长连接，并注册事件处理器。
    #  Start long connection and register event handler.
    wsClient.start()


if __name__ == "__main__":
    main()
