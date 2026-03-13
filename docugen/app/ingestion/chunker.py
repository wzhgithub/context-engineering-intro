"""文档分块模块。

将文档分割成适合嵌入的片段。
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ChunkingConfig:
    """分块配置。"""

    chunk_size: int = 512
    chunk_overlap: int = 50
    min_chunk_size: int = 50


@dataclass
class DocumentChunk:
    """文档片段。"""

    content: str
    index: int
    start_char: int
    end_char: int
    metadata: dict


def chunk_document(
    content: str,
    config: Optional[ChunkingConfig] = None,
    metadata: Optional[dict] = None,
) -> list[DocumentChunk]:
    """将文档分割成片段。

    Args:
        content: 文档内容
        config: 分块配置
        metadata: 元数据

    Returns:
        文档片段列表
    """
    if not content or not content.strip():
        return []

    config = config or ChunkingConfig()
    metadata = metadata or {}

    # 先按段落分割
    paragraphs = re.split(r"\n\s*\n", content)

    chunks = []
    current_chunk = ""
    current_start = 0
    chunk_index = 0
    char_position = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            char_position += 2  # 空行
            continue

        potential = current_chunk + "\n\n" + para if current_chunk else para

        if len(potential) <= config.chunk_size:
            current_chunk = potential
        else:
            # 保存当前片段
            if current_chunk and len(current_chunk) >= config.min_chunk_size:
                chunks.append(DocumentChunk(
                    content=current_chunk.strip(),
                    index=chunk_index,
                    start_char=current_start,
                    end_char=current_start + len(current_chunk),
                    metadata={**metadata, "chunk_index": chunk_index},
                ))
                chunk_index += 1

            # 开始新片段（带重叠）
            if len(para) > config.chunk_size:
                # 大段落需要进一步分割
                sub_chunks = _split_large_paragraph(
                    para, config, chunk_index, current_start, metadata
                )
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)
                current_chunk = ""
            else:
                current_chunk = para
                current_start = char_position

        char_position += len(para) + 2

    # 添加最后一个片段
    if current_chunk and len(current_chunk) >= config.min_chunk_size:
        chunks.append(DocumentChunk(
            content=current_chunk.strip(),
            index=chunk_index,
            start_char=current_start,
            end_char=current_start + len(current_chunk),
            metadata={**metadata, "chunk_index": chunk_index},
        ))

    return chunks


def _split_large_paragraph(
    text: str,
    config: ChunkingConfig,
    start_index: int,
    start_char: int,
    metadata: dict,
) -> list[DocumentChunk]:
    """分割大段落。

    Args:
        text: 段落文本
        config: 分块配置
        start_index: 起始索引
        start_char: 起始字符位置
        metadata: 元数据

    Returns:
        片段列表
    """
    chunks = []
    start = 0
    index = start_index

    while start < len(text):
        end = start + config.chunk_size

        if end >= len(text):
            chunk_text = text[start:]
            if len(chunk_text) >= config.min_chunk_size:
                chunks.append(DocumentChunk(
                    content=chunk_text.strip(),
                    index=index,
                    start_char=start_char + start,
                    end_char=start_char + len(text),
                    metadata={**metadata, "chunk_index": index},
                ))
            break

        # 尝试在句子边界结束
        chunk_end = end
        for i in range(end, max(start + config.min_chunk_size, end - 100), -1):
            if text[i] in ".!?。！？":
                chunk_end = i + 1
                break

        chunk_text = text[start:chunk_end]
        if len(chunk_text.strip()) >= config.min_chunk_size:
            chunks.append(DocumentChunk(
                content=chunk_text.strip(),
                index=index,
                start_char=start_char + start,
                end_char=start_char + chunk_end,
                metadata={**metadata, "chunk_index": index},
            ))
            index += 1

        # 重叠
        start = chunk_end - config.chunk_overlap

    return chunks
