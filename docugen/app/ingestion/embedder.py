"""嵌入生成模块。

生成文本的向量嵌入。
"""

import logging
import asyncio
from typing import Optional
from openai import AsyncOpenAI, RateLimitError

logger = logging.getLogger(__name__)


class Embedder:
    """嵌入生成器。"""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        base_url: Optional[str] = None,
        batch_size: int = 100,
        max_retries: int = 3,
    ):
        """初始化嵌入生成器。

        Args:
            api_key: OpenAI API 密钥
            model: 嵌入模型
            base_url: API 基础 URL
            batch_size: 批处理大小
            max_retries: 最大重试次数
        """
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model
        self.batch_size = batch_size
        self.max_retries = max_retries

    async def embed(self, text: str) -> list[float]:
        """生成单个文本的嵌入。

        Args:
            text: 输入文本

        Returns:
            嵌入向量
        """
        for attempt in range(self.max_retries):
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=text,
                )
                return response.data[0].embedding

            except RateLimitError:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                logger.error(f"嵌入生成失败: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(1)

        raise RuntimeError("嵌入生成失败")

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量生成嵌入。

        Args:
            texts: 文本列表

        Returns:
            嵌入向量列表
        """
        results = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]

            for attempt in range(self.max_retries):
                try:
                    response = await self.client.embeddings.create(
                        model=self.model,
                        input=batch,
                    )
                    results.extend([d.embedding for d in response.data])
                    break

                except RateLimitError:
                    if attempt == self.max_retries - 1:
                        # 回退到单独处理
                        for text in batch:
                            try:
                                embedding = await self.embed(text)
                                results.append(embedding)
                            except Exception:
                                results.append([0.0] * 1536)
                        break
                    await asyncio.sleep(2 ** attempt)

                except Exception as e:
                    logger.error(f"批量嵌入失败: {e}")
                    if attempt == self.max_retries - 1:
                        # 添加零向量作为回退
                        results.extend([[0.0] * 1536 for _ in batch])
                        break
                    await asyncio.sleep(1)

        return results
