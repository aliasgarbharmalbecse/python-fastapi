from datetime import datetime

# Utility: Get current quarter
def get_current_quarter(date: datetime) -> int:
    return (date.month - 1) // 3 + 1

# Utility: Calculate number of leave days
def calculate_days(from_date: datetime, to_date: datetime) -> int:
    return (to_date - from_date).days + 1