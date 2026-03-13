"""智能体抽象基类。

所有智能体必须实现此接口。基于 LangGraph 的节点函数模式，
每个智能体是一个可执行的状态转换函数。
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

StateT = TypeVar("StateT")

logger = logging.getLogger(__name__)


class BaseAgent(ABC, Generic[StateT]):
    """智能体抽象基类。

    所有智能体必须实现此接口。每个智能体是一个可执行的
    状态转换函数，接收当前状态并返回部分状态更新。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """智能体名称，用于日志和调试。"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """智能体功能描述。"""
        pass

    @abstractmethod
    async def __call__(
        self,
        state: StateT,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """执行智能体逻辑。

        必须返回部分状态更新，而不是完整状态。

        Args:
            state: 当前工作流状态
            config: 运行时配置

        Returns:
            部分状态更新字典
        """
        pass

    @abstractmethod
    def get_tools(self) -> list[Any]:
        """获取智能体可用的工具列表。

        Returns:
            工具列表
        """
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        """获取智能体的系统提示词。

        Returns:
            系统提示词字符串
        """
        pass

    def validate_input(self, state: StateT) -> bool:
        """验证输入状态是否有效。

        Args:
            state: 输入状态

        Returns:
            是否有效
        """
        return True

    def handle_error(self, error: Exception, state: StateT) -> dict[str, Any]:
        """错误处理回调。

        Args:
            error: 捕获的异常
            state: 当前状态

        Returns:
            错误状态更新
        """
        logger.error(f"[{self.name}] 错误: {error}")
        return {"error": str(error), "status": "failed"}
