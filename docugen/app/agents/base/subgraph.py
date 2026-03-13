"""子图抽象基类。

子图是一个独立的工作流，可以嵌入到父图中。
子图有自己的状态、节点和边。
"""

import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from langgraph.graph import CompiledGraph, StateGraph

StateT = TypeVar("StateT")

logger = logging.getLogger(__name__)


class BaseSubgraph(ABC, Generic[StateT]):
    """子图抽象基类。

    子图是一个独立的工作流，可以嵌入到父图中。
    子图有自己的状态、节点和边。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """子图名称。"""
        pass

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """构建子图结构。

        Returns:
            未编译的 StateGraph
        """
        pass

    @abstractmethod
    def get_state_schema(self) -> type[StateT]:
        """获取子图状态模式。

        Returns:
            状态 TypedDict 类
        """
        pass

    def compile(self, checkpointer=None) -> CompiledGraph:
        """编译子图。

        Args:
            checkpointer: 检查点保存器（子图通常从父图继承，不要手动传入）

        Returns:
            编译后的可执行图
        """
        logger.info(f"编译子图: {self.name}")
        graph = self.build_graph()
        return graph.compile(checkpointer=checkpointer)
