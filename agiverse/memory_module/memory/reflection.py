from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import litellm
import numpy as np
from dotenv import load_dotenv
from .base import Memory
from .manager import MemoryManager
from .spatial import SpatialMemory

load_dotenv()

class MemoryReflection:
    # To be used
    def _filter_by_time(self, memories: List[Memory],
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> List[Memory]:
        if not memories:
            return []
        if not start_time and not end_time:
            return memories
            
        filtered = memories.copy()
        if start_time:
            filtered = [m for m in filtered if m.created_at >= start_time]
        if end_time:
            filtered = [m for m in filtered if m.created_at <= end_time]
            
        return filtered

    # To be used
    def format_memories(self, memories: List[Memory]) -> List[Memory]:
        formatted_memories = []
        for memory in memories:
            formatted_memory = Memory(
                content=self._format_memory_content(memory.content),
                type=memory.type,
                created_at=memory.created_at,
                embedding=np.array([0.1] * 1536)
            )
            formatted_memories.append(formatted_memory)
        return formatted_memories
    # To be used
    def generate_summary(self, memories: List[Memory], 
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> str:
        if not memories:
            return "No memories to analyze"
            
        filtered_memories = self._filter_by_time(memories, start_time, end_time)
        if not filtered_memories:
            return "No memories in the specified time period"
            
        summary_points = []
        for memory in filtered_memories:
            content = memory.content
            if hasattr(memory, 'type'):
                summary_points.append(f"- {content} (Type: {memory.type})")
            else:
                summary_points.append(f"- {content}")
            
        return "\n".join(summary_points)


    def _format_memory_content(self, content: str) -> str:
        if not content:
            return ""
        
        parts = []
        current = ""
        for char in content:
            if char in ".!?":
                current += char
                if current.strip():
                    parts.append(current.strip())
                current = ""
            else:
                current += char
        if current.strip():
            parts.append(current.strip())
        
        formatted_parts = []
        for part in parts:
            words = part.split()
            if words:
                words[0] = words[0].capitalize()
                formatted = " ".join(words)
                if not formatted[-1] in ".!?":
                    formatted += "."
                formatted_parts.append(formatted)
            
        return " ".join(formatted_parts)

    async def compress_memory_content(self, memory: Memory, max_length: int = 500, model: str = None) -> str:
        prompt = f"""Please compress the following memory content while preserving key information. 
Keep the compressed version under {max_length} characters.

Original content:
{memory.content}

Return only the compressed content."""

        response = await litellm.acompletion(
            model=model or os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[{
                "role": "system",
                "content": "You are an expert at summarizing and compressing information while maintaining key details."
            },
            {
                "role": "user",
                "content": prompt
            }],
            temperature=0.3,
            max_tokens=max_length
        )

        try:
            compressed = response.choices[0].message.content.strip()
            return compressed[:min(len(compressed), max_length)]
        except (AttributeError, IndexError):
            return memory.content[:max_length]