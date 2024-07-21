from .nodes.calendar import CalendarNode
from .nodes.utils_node import CalendarUtilGetDate
from .nodes.calendar_solar_node import CalendarLunarSolarMouthNode
from  .nodes.calendar_lunar_node import CalendarLunarNode
NODE_CLASS_MAPPINGS = {
    "Calendar": CalendarNode,
    "CalendarUtilGetDate": CalendarUtilGetDate,
    "CalendarLunar": CalendarLunarNode,
    "CalendarSolarMouth": CalendarLunarSolarMouthNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Calendar": "生成日历",
    "CalendarUtilGetDate": "获取当前日期",
    "CalendarLunar": "生成农历日历-月历",
    "CalendarSolarMouth": "生成公历日历-月历"
}