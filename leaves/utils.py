import datetime

from .models import PublicHoliday


def calculate_working_days(start_date, end_date):
    """
    Count days between start_date and end_date (inclusive),
    excluding Saturdays, Sundays, and Public Holidays.
    """
    if end_date < start_date:
        return 0

    holiday_dates = set(
        PublicHoliday.objects.filter(
            date__gte=start_date, date__lte=end_date
        ).values_list('date', flat=True)
    )

    total = 0
    current = start_date
    while current <= end_date:
        is_weekend = current.weekday() >= 5  # 5=Saturday, 6=Sunday
        if not is_weekend and current not in holiday_dates:
            total += 1
        current += datetime.timedelta(days=1)

    return total
