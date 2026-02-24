# 快速测试指南

## 步骤 1：启动机器人并获取 chat_id

1. 启动机器人程序：
   ```bash
   python lark_bot.py
   ```

2. 在飞书客户端中：
   - 搜索「自动回复机器人」
   - 给机器人发送一条消息，例如："你好"

3. 在机器人的控制台输出中，找到类似这样的日志：
   ```
   chat_id: oc_xxxxxxxxxxxxx
   ```
   复制这个 chat_id

## 步骤 2：使用 chat_id 进行自动化测试

运行测试脚本：
```bash
python send_test_message.py oc_xxxxxxxxxxxxx "测试消息"
```

替换 `oc_xxxxxxxxxxxxx` 为你在步骤 1 中获取的 chat_id。

## 步骤 3：验证机器人回复

测试脚本会：
1. 发送测试消息给机器人
2. 等待 10 秒
3. 检查机器人是否回复
4. 输出测试结果

## 完整的自动化测试

如果你想运行完整的测试（包括验证回复），使用：
```bash
# 修改 test_bot_message.py 中的 CHAT_ID
# 然后运行
python test_bot_message.py
```

## 注意事项

- 确保机器人程序正在运行
- 确保机器人有权限发送消息
- chat_id 在每次新建会话时会变化
- 如果测试失败，检查机器人日志中的错误信息
