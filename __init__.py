from .nodes.calendar import CalendarNode
from .nodes.utils_node import CalendarUtilGetDate
from .nodes.calendar_lunar_node import CalendarLunarNode
from .nodes.calendar_solar_node import CalendarLunarSolarMouthNode

NODE_CLASS_MAPPINGS = {
    "Calendar": CalendarNode,
    "CalendarUtilGetDate": CalendarUtilGetDate,
    "CalendarLunar": CalendarLunarNode,
    "CalendarSolarMouth": CalendarLunarSolarMouthNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Calendar": "📅 生成日历",
    "CalendarUtilGetDate": "📅 获取时间",
    "CalendarLunar": "📅 生成农历月历",
    "CalendarSolarMouth": "📅 生成公历日历"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
