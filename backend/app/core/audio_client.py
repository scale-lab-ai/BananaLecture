import os
import json
import asyncio
from typing import Optional, Dict, Any
import logging
import httpx
import binascii
import random

from app.config import config_manager

logger = logging.getLogger(__name__)


class AudioClient:
    """AI音频请求客户端类，负责处理AI音频生成请求，内置重试等功能"""

    def __init__(self, max_retries: int = 3, base_delay: float = 5.0, max_delay: float = 60.0, exponential_base: float = 2.0):
        """Initialize audio client with configuration and retry parameters

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            exponential_base: Base for exponential backoff calculation
        """
        # Load configuration
        config = config_manager.get_config()

        # 初始化MiniMax API配置
        self.group_id = config.env.MINIMAX_AUDIO_GROUP_ID
        self.api_key = config.env.MINIMAX_AUDIO_API_KEY
        self.model = config.env.MINIMAX_AUDIO_MODEL
        self.url = f"https://api.minimax.chat/v1/t2a_v2?GroupId={self.group_id}"

        # 语速映射
        self.speed_map = {
            "慢": 0.8,
            "正常": 1.0,
            "快": 1.25
        }

        # 音频设置
        self.audio_setting = {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3"
        }

        # 基础payload模板
        self.base_payload = {
            "model": self.model,
            "timbre_weights": [
                {
                    "voice_id": "",  # 将在具体方法中设置
                    "weight": 100
                }
            ],
            "voice_setting": {
                "voice_id": "",
                "speed": 1.0,  # 将在具体方法中设置
                "pitch": 0,
                "vol": 1,
                "latex_read": True
            },
            "audio_setting": self.audio_setting,
            "language_boost": "auto"
        }

        # Retry configuration
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

        # 创建httpx客户端
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.client.aclose()

    def _is_api_response_valid(self, result: Dict[str, Any]) -> tuple:
        """检查API响应是否有效

        Args:
            result: API响应结果

        Returns:
            (is_valid, error_message) 元组
        """
        if "base_resp" not in result:
            return False, "API响应中缺少'base_resp'字段"

        base_resp = result["base_resp"]
        status_code = base_resp.get("status_code", -1)
        status_msg = base_resp.get("status_msg", "")

        if status_code != 0:
            return False, f"API返回错误码 {status_code}: {status_msg}"

        if "data" not in result or result["data"] is None:
            return False, "API响应中缺少'data'字段或data为null"

        if "audio" not in result["data"]:
            return False, "API响应中缺少'audio'字段"

        return True, ""

    async def generate_audio(self, text: str, role: str, emotion: str, speed: str) -> Optional[bytes]:
        """Generate audio from text using AI service

        Args:
            text: Text to convert to audio
            role: Character role for voice selection
            emotion: Emotion for the audio
            speed: Speed of the audio ("慢", "正常", "快")
            is_gadgets: Whether this is a gadget audio

        Returns:
            Audio bytes data, None if failed
        """
        payload = await self._build_payload(text, role, emotion, speed)
        return await self._request_audio(payload)

    async def _build_payload(self, text: str, role: str, emotion: str, speed: str) -> Dict[str, Any]:
        """构建请求payload

        Args:
            text: 文本内容
            role: 角色名称
            emotion: 情感
            speed: 语速

        Returns:
            构建好的payload
        """
        # 复制基础payload
        payload = json.loads(json.dumps(self.base_payload))

        # 设置文本
        payload["text"] = text

        # 设置角色
        role_voice_map = config_manager.get_current_role_voice()

        if role == "道具" and config_manager.get_current_group() == "Doraemon":
            voice_id = role_voice_map.get("哆啦A梦", role_voice_map.get("其他", "Chinese (Mandarin)_Radio_Host"))
            payload["voice_setting"]["emotion"] = "happy"
            payload["voice_setting"]["latex_read"] = False
        else:
            voice_id = role_voice_map.get(role, role_voice_map.get("其他", "Chinese (Mandarin)_Radio_Host"))
            payload["voice_setting"]["latex_read"] = True

        payload["voice_setting"]["speed"] = self.speed_map.get(speed, 1.0)
        payload["timbre_weights"][0]["voice_id"] = voice_id

        if emotion != "auto":
            payload["voice_setting"]["emotion"] = emotion

        return payload

    async def _request_audio(self, payload: Dict[str, Any]) -> Optional[bytes]:
        """发送请求获取音频数据

        Args:
            payload: 请求payload

        Returns:
            音频字节数据，失败时返回None
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                response = await self.client.post(self.url, json=payload)

                # Check for HTTP errors
                if response.status_code == 429:  # Rate limit
                    logger.warning(f"Rate limited (attempt {attempt}/{self.max_retries}), waiting before retry...")
                    if attempt < self.max_retries:
                        await self._exponential_backoff(attempt)
                        continue
                    else:
                        logger.error("Rate limit exceeded and no more retries left")
                        return None
                elif 400 <= response.status_code < 500:
                    logger.error(f"Client error {response.status_code}: {response.text}")
                    return None  # Don't retry client errors
                elif response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code} (attempt {attempt}/{self.max_retries})")

                response.raise_for_status()
                result = response.json()

                is_valid, error_message = self._is_api_response_valid(result)
                if not is_valid:
                    logger.warning(f"API响应验证失败（第{attempt}次尝试）: {error_message}")

                    if attempt < self.max_retries:
                        await self._exponential_backoff(attempt)
                        continue
                    else:
                        logger.error(f"重试次数耗尽，API响应验证失败: {error_message}")
                        return None

                audio_bytes = binascii.unhexlify(result["data"]["audio"])
                await asyncio.sleep(5)  # Throttle requests
                return audio_bytes

            except httpx.TimeoutException as e:
                logger.warning(f"请求超时（第{attempt}次尝试）: {str(e)}")
                if attempt < self.max_retries:
                    await self._exponential_backoff(attempt)
                else:
                    logger.error(f"重试次数耗尽，请求超时: {str(e)}")
                    return None

            except httpx.HTTPError as e:
                logger.warning(f"HTTP请求失败（第{attempt}次尝试）: {str(e)}")
                if attempt < self.max_retries:
                    await self._exponential_backoff(attempt)
                else:
                    logger.error(f"重试次数耗尽，HTTP请求最终失败: {str(e)}")
                    return None

            except (binascii.Error, ValueError, KeyError) as e:
                logger.warning(f"音频数据处理失败（第{attempt}次尝试）: {str(e)}")
                if attempt < self.max_retries:
                    await self._exponential_backoff(attempt)
                else:
                    logger.error(f"重试次数耗尽，音频数据处理最终失败: {str(e)}")
                    return None
            except Exception as e:
                logger.warning(f"未知错误（第{attempt}次尝试）: {str(e)}")
                if attempt < self.max_retries:
                    await self._exponential_backoff(attempt)
                else:
                    logger.error(f"重试次数耗尽，未知错误: {str(e)}")
                    return None

        return None

    async def _exponential_backoff(self, attempt: int) -> None:
        """计算并执行指数退避延迟

        Args:
            attempt: 当前尝试次数
        """
        # 计算延迟时间：base_delay * (exponential_base ^ attempt) + random jitter
        delay = min(self.base_delay * (self.exponential_base ** (attempt - 1)), self.max_delay)
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0, 0.1 * delay)
        total_delay = delay + jitter

        logger.info(f"等待 {total_delay:.2f} 秒后重试...")
        await asyncio.sleep(total_delay)