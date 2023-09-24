from datetime import datetime
import pytz


async def time_format_is_correct(time_to_parse):
    try:
        time = datetime.strptime(time_to_parse, "%H:%M:%S").time()
        return True
    except:
        print(f"The value '{time_to_parse}' does not match the time format '%H:%M:%S'")
    return False


async def timezone_exists(timezone):
    if timezone in pytz.all_timezones:
        return True
    print(f"The timezone '{timezone}' does not exist")
    return False
