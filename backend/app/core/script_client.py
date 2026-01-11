import asyncio
import logging
from typing import List, Literal
from app.models.enums import EmotionType, SpeechSpeed

from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.config import config_manager

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """你是一个专业的口播稿生成助手,你需要根据已经生成的口播稿上下文,将提供的图片转换为生动有趣的对话稿。

要求：
1. 角色可以是{roles}，确保角色与对话内容严格对齐
2. 内容要简洁明了，适合口头表达
3. 语言要生动有趣，吸引听众
4. 为每个对话项设置合适的情感和语速

注意事项:
1. 图片中所有出现的公式与数学符号均转化为Latex格式,并都用$$包裹,如$$E = m \\times c^2$$与$$1-\\epsilon$$
"""


# Doraemon specific system prompt
SYSTEM_PROMPT_DORAEMON = "2. 道具为特殊role，当且仅当哆啦A梦首次掏出道具时，添加角色为道具内容为道具名称的对话，后续出现时无需重复添加(**仅添加一次即可**),封面页禁止生成道具角色"


class DialogueItemAI(BaseModel):
    """AI model for dialogue items, automatically validated by Pydantic AI"""
    role: str = Field(..., description="说话的角色名称")
    content: str = Field(..., description="口播稿具体内容")
    emotion: EmotionType = Field(default=EmotionType.AUTO, description="对话的情感, 若未表现出明显情感, 则为auto")
    speed: SpeechSpeed = Field(default=SpeechSpeed.NORMAL, description="对话的语速")


class ScriptClient:
    """Client for interacting with the AI to generate scripts."""

    async def _retry_with_exponential_backoff(self, coro_func, max_retries: int = 3, base_delay: float = 5.0):
        """
        Retries an async function with exponential backoff.

        Args:
            coro_func: The async coroutine function to call.
            max_retries: Maximum number of retries.
            base_delay: The base delay in seconds.

        Returns:
            The result of the coroutine function.

        Raises:
            Exception: Raises the last exception after all retries fail.
        """
        for attempt in range(1, max_retries + 1):
            try:
                return await coro_func()
            except Exception as e:
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error("All retries failed.")
                    raise

    async def generate_script_for_image(
            self, prompt: str, image_bytes: bytes, max_retries: int = 3
    ) -> List[DialogueItemAI]:
        """
        Generates a script for a given image and prompt using the AI agent.

        Args:
            prompt: The text prompt to guide the generation.
            image_bytes: The image content as bytes.
            max_retries: The maximum number of times to retry the request.

        Returns:
            A list of DialogueItemAI objects representing the generated script.
        """
        config = config_manager.get_config()
        current_group = config_manager.get_current_group()
        role_list = list(config_manager.get_current_role_voice().keys())
        if current_group == "Doraemon":
            role_list.append("道具")
        model = OpenAIChatModel(
            config.env.LLM_OPENAI_MODEL,
            provider=OpenAIProvider(api_key=config.env.LLM_OPENAI_API_KEY, base_url=config.env.LLM_OPENAI_BASE_URL)
        )

        class DialogueItemOutput(DialogueItemAI):
            @field_validator("role")
            @classmethod
            def validate_role(cls, v):
                if v not in role_list:
                    raise ValueError(f"无效的角色 '{v}'。允许的角色: {', '.join(role_list)}")
                return v

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(roles=", ".join(role_list))
        if current_group == "Doraemon":
            system_prompt += "\n" + SYSTEM_PROMPT_DORAEMON

        self.agent = Agent(
            model=model,
            output_type=List[DialogueItemOutput],
            system_prompt=system_prompt,
        )

        async def run_agent():
            result = await self.agent.run([
                prompt,
                BinaryContent(media_type="image/png", data=image_bytes)
            ])
            return result.output

        return await self._retry_with_exponential_backoff(run_agent, max_retries=max_retries)

