REDIS_KEY_USER_VERSION = "user:{user_id}:version"
REDIS_KEY_STATS_BASE = "stats:{user_id}:base"
REDIS_KEY_STATS_CATEGORIES = "stats:{user_id}:categories"
REDIS_KEY_FILE_HASH = "file:hash:{hash}"
REDIS_KEY_LAST_FILE_UPLOAD = "user:{user_id}:last_upload"

CACHE_TTL_STATS = 86400  # 24 hours
CACHE_TTL_CATEGORIES = 86400  # 24 hours
CACHE_TTL_FILE_HASH = 1209600  # 14 days

MAX_FILE_SIZE_MB = 50
MAX_OPERATIONS_PER_FILE = 10000

BANK_TINKOFF = "tinkoff"
BANK_ALFA = "alfa"
BANK_SBER = "sber"

SUPPORTED_BANKS = [BANK_TINKOFF, BANK_ALFA, BANK_SBER]

QUEUE_HIGH = "high"
QUEUE_DEFAULT = "default"
QUEUE_LOW = "low"
QUEUE_CELERY = "celery"
