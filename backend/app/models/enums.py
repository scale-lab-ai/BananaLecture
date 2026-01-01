from enum import Enum


class TaskType(str, Enum):
    SCRIPT_GENERATION = "script_generation"
    AUDIO_GENERATION = "audio_generation"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DialogueRole(str, Enum):
    NARRATOR = "旁白"
    DAXIONG = "大雄"
    DUOLAAMENG = "哆啦A梦"
    PROP = "道具"
    OTHER_MALE = "其他男声"
    OTHER_FEMALE = "其他女声"
    OTHER = "其他"


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