"""
响应格式化器
"""
from typing import Optional


class ResponseFormatter:
    """格式化响应消息，包含原始问题和执行结果"""
    
    def format_response(
        self,
        user_message: str,
        ai_output: str,
        error: Optional[str] = None
    ) -> str:
        """格式化响应消息
        
        Args:
            user_message: 用户原始消息
            ai_output: AI 输出内容
            error: 错误信息（可选）
            
        Returns:
            格式化后的响应消息
        """
        if error:
            return self.format_error(user_message, error)
        
        return (
            f"收到你发送的消息：{user_message}\n"
            f"Received message: {user_message}\n\n"
            f"AI 输出：\n{ai_output}"
        )
    
    def format_error(self, user_message: str, error_message: str) -> str:
        """格式化错误消息
        
        Args:
            user_message: 用户原始消息
            error_message: 错误信息
            
        Returns:
            格式化后的错误消息
        """
        return (
            f"收到你发送的消息：{user_message}\n"
            f"Received message: {user_message}\n\n"
            f"执行失败：{error_message}"
        )
