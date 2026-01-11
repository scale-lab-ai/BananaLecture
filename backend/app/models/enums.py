from enum import Enum


class TaskType(str, Enum):
    SCRIPT_GENERATION = "script_generation"
    AUDIO_GENERATION = "audio_generation"
    PDF_CONVERSION = "pdf_conversion"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EmotionType(str, Enum):
    AUTO = "auto"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    SURPRISED = "surprised"
    NEUTRAL = "neutral"
    FLUENT = "fluent"


class SpeechSpeed(str, Enum):
    SLOW = "慢"
    NORMAL = "正常"
    FAST = "快"