from datetime import datetime

class CalendarUtilGetDate: 
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {}
        }

    RETURN_TYPES = ("INT", "INT", "INT", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("year", "month", "day", "year_str", "month_str", "day_str")
    FUNCTION = "calendar_util_get_date"
    CATEGORY = "日历"

    def calendar_util_get_date(self):
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        # string date
        year_str = str(year)
        month_str = str(month)
        day_str = str(day)
        return year, month, day, year_str, month_str, day_str
