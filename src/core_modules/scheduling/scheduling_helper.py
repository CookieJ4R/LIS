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
    if repeat_policy is EventRepeatPolicy.Hourly:
        return get_next_hour_for_date(exec_time)
    elif repeat_policy is EventRepeatPolicy.Daily:
        return get_next_day_for_date(exec_time)
    elif repeat_policy is EventRepeatPolicy.Weekly:
        return get_next_week_for_date(exec_time)
    elif repeat_policy is EventRepeatPolicy.Monthly:
        return get_next_month_for_date(exec_time)
    elif repeat_policy is EventRepeatPolicy.Yearly:
        return get_next_year_for_date(exec_time)


def get_next_hour_for_date(old_datetime: datetime):
    """
    Calculates a date for the passed datetime + 1 hour.
    :param old_datetime: The old datetime.
    :return: The old datetime plus 1 hour.
    """
    return old_datetime + timedelta(hours=1)


def get_next_day_for_date(old_datetime: datetime):
    """
    Calculates a date for the passed datetime + 1 day.
    :param old_datetime: The old datetime.
    :return: The old datetime plus 1 day.
    """
    return old_datetime + timedelta(days=1)


def get_next_week_for_date(old_datetime: datetime):
    """
    Calculates a date for the passed datetime + 1 week.
    :param old_datetime: The old datetime.
    :return: The old datetime plus 1 week.
    """
    return old_datetime + timedelta(weeks=1)


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
