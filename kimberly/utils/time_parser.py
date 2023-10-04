from datetime import datetime
import pytz


async def time_format_is_correct(time_to_parse):
    try:
        datetime.strptime(time_to_parse, "%H:%M:%S").time()
        return True
    except:
        print(f"The value '{time_to_parse}' does not match the time format '%H:%M:%S'")
    return False


async def date_format_is_correct(date_to_parse):
    try:
        datetime.strptime(date_to_parse, "%m-%d").date()
        return True
    except:
        print(f"The value '{date_to_parse}' does not match the date format '%m-%d'")
    return False


async def timezone_exists(timezone):
    if timezone in pytz.all_timezones:
        return True
    print(f"The timezone '{timezone}' does not exist")
    return False
