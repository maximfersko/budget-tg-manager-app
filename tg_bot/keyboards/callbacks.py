"""Callback data constants for inline keyboards."""

# Prefixes
BANK_PREFIX = "bank_"
STATS_PREFIX = "stats_"
OPERATION_PREFIX = "op_"

# Banks
BANK_TINKOFF = f"{BANK_PREFIX}tinkoff"
BANK_ALFA = f"{BANK_PREFIX}alfa"
BANK_SBER = f"{BANK_PREFIX}sber"

# Statistics periods
STATS_MONTH = f"{STATS_PREFIX}month"
STATS_YEAR = f"{STATS_PREFIX}year"
STATS_CUSTOM = f"{STATS_PREFIX}custom"

# Operation actions
OP_EDIT = f"{OPERATION_PREFIX}edit"
OP_DELETE = f"{OPERATION_PREFIX}delete"
OP_CANCEL = f"{OPERATION_PREFIX}cancel"
