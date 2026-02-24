"""
Gemini API 执行器实现

调用 Google Gemini API 执行 AI 任务。
支持对话历史上下文（使用 chat 模式）和可选参数配置。

参考文档: https://ai.google.dev/api/python/google/generativeai
"""
import time
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from feishu_bot.ai_api_executor import AIAPIExecutor
from feishu_bot.models import ExecutionResult, Message


class GeminiAPIExecutor(AIAPIExecutor):
    """Gemini API 执行器
    
    使用 Google AI Python SDK 调用 Gemini API。
    支持多轮对话上下文（chat 模式）和灵活的参数配置。
    
    Requirements: 14.2, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9, 14.10, 15.1, 15.3, 15.5, 15.6
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp",
        timeout: int = 60
    ):
        """初始化 Gemini API 执行器
        
        Args:
            api_key: Google AI API 密钥
            model: Gemini 模型名称，默认使用最新的实验版 Flash 模型
            timeout: 请求超时时间（秒）
        """
        super().__init__(api_key, model, timeout)
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)
    
    def get_provider_name(self) -> str:
        """返回 AI 提供商名称
        
        Returns:
            "gemini-api"
        """
        return "gemini-api"
    
    def format_messages(
        self,
        user_prompt: str,
        conversation_history: Optional[List[Message]] = None
    ) -> List[Dict[str, Any]]:
        """格式化为 Gemini API 消息格式
        
        Gemini API 使用 "user" 和 "model" 角色（注意：assistant 需要转换为 model）。
        消息格式为 {"role": "user"/"model", "parts": [content]}
        
        Args:
            user_prompt: 用户提示
            conversation_history: 对话历史
            
        Returns:
            格式化后的消息列表，每个消息包含 role 和 parts 字段
        """
        messages = []
        
        # 添加对话历史
        if conversation_history:
            for msg in conversation_history:
                # Gemini API 使用 "model" 而不是 "assistant"
                role = "user" if msg.role == "user" else "model"
                messages.append({
                    "role": role,
                    "parts": [msg.content]
                })
        
        # 添加当前用户消息
        messages.append({
            "role": "user",
            "parts": [user_prompt]
        })
        
        return messages
    
    def execute(
        self,
        user_prompt: str,
        conversation_history: Optional[List[Message]] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """调用 Gemini API 执行任务
        
        Args:
            user_prompt: 用户提示
            conversation_history: 对话历史（用于上下文）
            additional_params: 额外参数，支持：
                - temperature: 温度参数
                - max_tokens: 最大输出 token 数（映射到 max_output_tokens）
                
        Returns:
            ExecutionResult: 包含执行结果的对象
        """
        try:
            # 构建生成配置
            generation_config = {}
            if additional_params:
                if "temperature" in additional_params:
                    generation_config["temperature"] = additional_params["temperature"]
                if "max_tokens" in additional_params:
                    generation_config["max_output_tokens"] = additional_params["max_tokens"]
            
            # 如果有对话历史，使用 chat 模式
            if conversation_history:
                # 构建历史消息（不包含当前用户消息）
                history = [
                    {
                        "role": "user" if msg.role == "user" else "model",
                        "parts": [msg.content]
                    }
                    for msg in conversation_history
                ]
                
                chat = self.client.start_chat(history=history)
                start_time = time.time()
                response = chat.send_message(
                    user_prompt,
                    generation_config=generation_config if generation_config else None
                )
                execution_time = time.time() - start_time
            else:
                # 单次生成
                start_time = time.time()
                response = self.client.generate_content(
                    user_prompt,
                    generation_config=generation_config if generation_config else None
                )
                execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=True,
                stdout=response.text,
                stderr="",
                error_message=None,
                execution_time=execution_time
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                error_message=f"Gemini API error: {e}",
                execution_time=0
            )
