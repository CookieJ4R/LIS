"""
Class containing helper functions used for scheduling.
"""
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from core_modules.scheduling.EventRepeatPolicy import EventRepeatPolicy


def get_next_execution_time_for_policy(exec_time: datetime, repeat_policy: EventRepeatPolicy) -> datetime:
    """
    Function to get the next execution time based on the last execution time and the repeat policy.
    :param exec_time: The old execution time.
    :param repeat_policy: The repeat policy to schedule the next execution time for.
    :return: The next execution time
    """
    if repeat_policy is EventRepeatPolicy.QuarterHourly:
        return get_next_quarter_hour_for_date(exec_time)
    elif repeat_policy is EventRepeatPolicy.HalfHourly:
        return get_next_half_hour_for_date(exec_time)
    elif repeat_policy is EventRepeatPolicy.Hourly:
        return get_next_hour_for_date(exec_time)
    elif repeat_policy is EventRepeatPolicy.Daily:
        return get_next_day_for_date(exec_time)
    elif repeat_policy is EventRepeatPolicy.Weekly:
        return get_next_week_for_date(exec_time)
    elif repeat_policy is EventRepeatPolicy.Monthly:
        return get_next_month_for_date(exec_time)
    elif repeat_policy is EventRepeatPolicy.Yearly:
        return get_next_year_for_date(exec_time)


def get_next_quarter_hour_for_date(old_datetime: datetime):
    """
    Calculates a date for the passed datetime + 15 min.
    :param old_datetime: The old datetime.
    :return: The old datetime plus 15 min.
    """
    return old_datetime + relativedelta(minutes=15)


def get_next_half_hour_for_date(old_datetime: datetime):
    """
    Calculates a date for the passed datetime + 30 min.
    :param old_datetime: The old datetime.
    :return: The old datetime plus 30 min.
    """
    return old_datetime + relativedelta(minutes=30)


def get_next_hour_for_date(old_datetime: datetime):
    """
    Calculates a date for the passed datetime + 1 hour.
    :param old_datetime: The old datetime.
    :return: The old datetime plus 1 hour.
    """
    return old_datetime + relativedelta(hours=1)


def get_next_day_for_date(old_datetime: datetime):
    """
    Calculates a date for the passed datetime + 1 day.
    :param old_datetime: The old datetime.
    :return: The old datetime plus 1 day.
    """
    return old_datetime + relativedelta(days=1)


def get_next_week_for_date(old_datetime: datetime):
    """
    Calculates a date for the passed datetime + 1 week.
    :param old_datetime: The old datetime.
    :return: The old datetime plus 1 week.
    """
    return old_datetime + relativedelta(weeks=1)


def get_next_month_for_date(old_datetime: datetime):
    """
    Calculates a date for the passed datetime + 1 month.
    :param old_datetime: The old datetime.
    :return: The old datetime plus 1 month.
    """
    return old_datetime + relativedelta(months=1)


def get_next_year_for_date(old_datetime: datetime):
    """
    Calculates a date for the passed datetime + 1 year.
    :param old_datetime: The old datetime.
    :return: The old datetime plus 1 year.
    """
    return old_datetime + relativedelta(years=1)


def get_next_full_hour(datetime_now=datetime.now()):
    """
    Returns a datetime for the next full hour based on the current time (minutes = seconds = microseconds = 0)
    :return: A datetime for the next full hour.
    """
    new_date = datetime_now + relativedelta(hours=1)
    return new_date.replace(minute=0, second=0, microsecond=0)


def get_next_quarter_hour():
    """
    Returns a datetime for the next quarter of an hour based on the current time (seconds = microseconds = 0)
    :return: A datetime for the next quarter of the current hout.
    """
    now = datetime.now()
    quarters = [15, 30, 45]
    for match in quarters:
        if now.minute < match:
            return now.replace(minute=match, second=0, microsecond=0)
    return get_next_full_hour(now)
