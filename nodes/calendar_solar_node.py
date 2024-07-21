from datetime import datetime
from lunar_python import Lunar, Solar,LunarMonth,SolarMonth, Holiday
from lunar_python.util import  HolidayUtil
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from .util import pil2tensor
import glob
import os
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

root_dir = os.path.join(CURRENT_DIR, '..')

default_font_dir = os.path.join(root_dir, 'fonts')

default_font = 'Alibaba-PuHuiTi-Heavy.ttf'

__font_file_list = glob.glob(default_font_dir + '/*.ttf')
__font_file_list.extend(glob.glob(default_font_dir + '/*.otf'))
FONT_DICT = {}
for i in range(len(__font_file_list)):
    _, __filename =  os.path.split(__font_file_list[i])
    FONT_DICT[__filename] = __font_file_list[i]
FONT_LIST = list(FONT_DICT.keys())

class Day:
    def __init__(self):
        self.month = 0
        self.day = 0
        self.text = ''
        self.lunarDay = ''
        self.lunarMonth = ''
        self.lunarYear = ''
        self.yearGanZhi = ''
        self.yearShengXiao = ''
        self.monthGanZhi = ''
        self.dayGanZhi = ''
        self.isFestival = False
        self.isToday = False
        self.isHoliday = False
        self.isRest = False
        self.festivals = []

class Week:
    def __init__(self):
        self.days = []

class Month:
    def __init__(self):
        self.heads = []
        self.weeks = []

class Holiday:
    def __init__(self):
        self.name = ''
        self.month = 0

class CalendarLunarSolarMouthNode:
    """A node that displays a calendar with lunar dates."""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "year": ("INT", {"default": 2021, "min": 1900, "max": 2100}),
                "month": ("INT", {"default": 1, "min": 1, "max": 12}),
                "cell_size": ("INT", {"default": 100, "min": 1, "max": 9999}),
                "header_height": ("INT", {"default": 100, "min": 1, "max": 9999}),
                "row_padding": ("INT", {"default": 20, "min": 1, "max": 9999}),
                "header_font_size": ("INT", {"default": 36, "min": 1, "max": 9999}),
                "cell_font_size": ("INT", {"default": 24, "min": 1, "max": 9999}),
                "header_font_color": ("STRING", {"default": "white"}),
                "cell_color": ("STRING", {"default": "white"}),
                "background_color": ("STRING", {"default": "white"}),
                "font": np.array(FONT_LIST)
            },
        }
    
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = 'calendar_lunar'
    CATEGORY = '日历'

    def calendar_lunar(self, year, month, cell_size, header_height, row_padding, header_font_size, cell_font_size, header_font_color, cell_color, background_color, font):
        date_now = datetime.now()
        now = Solar.fromYmd(year, month, date_now.day)

        state = {
            'year':year,
            'month': month,
            'weekStart': 1,
            # type Month
            'data': Month(),
            'holidays': [],
            'holidayMonth': 0,
            'yearInGanZhi': '',
            'yearShengXiao': '',
            'monthInChinese': '',
            'monthInGanZhi': '',
        }

        self.render_data(state, now)

        print(state)

        return self.draw_image(state, cell_size, header_height, row_padding, header_font_size, cell_font_size, header_font_color, cell_color, background_color, font)

    def build_day(self, now:Solar, d: Solar):
        ymd = d.toYmd()
        lunar = d.getLunar()
        day = Day()
        day.month = d.getMonth()
        day.day = d.getDay()
        day.lunarMonth = lunar.getMonthInChinese()
        day.lunarDay = lunar.getDayInChinese()
        day.yearGanZhi = lunar.getYearInGanZhi()
        day.yearShengXiao = lunar.getYearShengXiao()
        day.monthGanZhi = lunar.getMonthInGanZhi()
        day.dayGanZhi = lunar.getDayInGanZhi()
        day.ymd = ymd
        day.isToday = ymd == now.toYmd()

        solarFestival = d.getFestivals()
        for f in solarFestival:
            day.festivals.append(f)

        otherFestivals = d.getOtherFestivals()
        for f in otherFestivals:
            day.festivals.append(f)

        lunarFestival = lunar.getFestivals()
        for f in lunarFestival:
            day.festivals.append(f)

        lunarOtherFestivals = lunar.getOtherFestivals()
        for f in lunarOtherFestivals:
            day.festivals.append(f)

        rest = False
        if d.getWeek() == 6 or d.getWeek == 0:
            rest = True
        
        holiday = HolidayUtil.getHoliday(ymd)
        if holiday:
            rest = not holiday.isWork()

        day.isHoliday = holiday
        day.isRest = rest

        desc = lunar.getDayInChinese()
        jq = lunar.getJieQi()

        if jq:
            desc = jq
        elif lunar.getDay() == 1:
            desc = lunar.getMonthInChinese() + '月'
        elif len(solarFestival) > 0:
            f = solarFestival[0]
            if len(f) < 4:
                desc = f
        
        day.desc = desc

        return day
    
    def render_data(self, state, now: Solar):
        month = Month()
        weeks = []
        solarWeeks = SolarMonth.fromYm(int(state['year']), int(state['month'])).getWeeks(state['weekStart'])
        for w in solarWeeks:
            weeks.append(w)

        while len(weeks) < 5:
            weeks.append(weeks[len(weeks) - 1].next(1, False))

        for w in weeks:
            week = Week()
            heads = []
            for d in w.getDays():
                heads.append(d.getWeekInChinese())
                week.days.append(self.build_day(now, d))
            month.heads.append(heads)
            month.weeks.append(week)

        state['data'] = month
        holidays = []
        for h in HolidayUtil.getHolidays(int(state['year'])):
            holiday = Holiday()
            holiday.name = h.getName()
            # parseInt(h.getTarget().substring(5, 7), 10) => python
            holiday.month = int(h.getTarget()[5:7])
            
            exists = False
            for a in holidays:
                if a.name == holiday.name:
                    exists = True
                    break

            if not exists:
                holidays.append(holiday)

        lunar = Lunar.fromYmd(state['year'], state['month'], 1)

        state['holidays'] = holidays
        state['yearInChinese'] = lunar.getYearInChinese()
        state['yearInGanZhi'] = lunar.getYearInGanZhi()
        state['yearShengXiao'] = lunar.getYearShengXiao()
        state['monthInChinese'] = lunar.getMonthInChinese()
        state['monthInGanZhi'] = lunar.getMonthInGanZhi()
            
    def draw_image(self, state,  cell_size, header_height, row_padding, header_font_size, cell_font_size, header_font_color, cell_color, background_color, font):
        cell_width = cell_size
        cell_height = cell_size
        padding = row_padding
        header_height = header_height

         # 创建一个新的空白图像
        img_width = cell_width * 7 + padding * 2
        img_height = cell_height * 5 + padding * 2 + header_height
        image = Image.new('RGBA', size=(img_width, img_height), color=background_color)
        draw = ImageDraw.Draw(image)

        # 加载字体
        font_path = font
        font = ImageFont.truetype(font_path, header_font_size)
        font_small = ImageFont.truetype(font_path, cell_font_size)

        # 绘制表头
        header_text = f"{state['year']}年{state['month']}月 · {state['yearInGanZhi']}年{state['monthInChinese']}月"
        header_bbox = draw.textbbox((0, 0), header_text, font=font)
        header_width = header_bbox[2] - header_bbox[0]
        header_height_text = header_bbox[3] - header_bbox[1]
        draw.text(((img_width - header_width) / 2, padding), header_text, fill=header_font_size, font=font)

        # 绘制星期表头
        days_of_week = state['data'].heads[0]
        print(f"days_of_week: {days_of_week}")
        for i, day in enumerate(days_of_week):
            x = padding + i * cell_width
            y = header_height
            day_bbox = draw.textbbox((0, 0), day, font=font_small)
            day_width = day_bbox[2] - day_bbox[0]
            draw.text((x + (cell_width - day_width) / 2, y), day, fill=header_font_color, font=font_small)

         # 按照week绘制日历 天
        for week_index, week in enumerate(state['data'].weeks):
            print(f"week_index: {week_index}")
            print(f"week: {week}")
            for day_index, day in enumerate(week.days):
                print(f"day_index: {day_index}")
                print(f"day: {day}")

                x = padding + day_index * cell_width
                y = padding + (week_index + 1) * cell_height + 20  # 调整位置，确保第一行紧贴星期表头

                lunar_day_bbox = draw.textbbox((0, 0), str(day.day), font=font_small)
                lunar_day_width = lunar_day_bbox[2] - lunar_day_bbox[0]
                lunar_day_height = lunar_day_bbox[3] - lunar_day_bbox[1]

                desc_bbox = draw.textbbox((0, 0), day.desc, font=font_small)
                desc_width = desc_bbox[2] - desc_bbox[0]
                desc_height = desc_bbox[3] - desc_bbox[1]

                draw.text((x + (cell_width - lunar_day_width) / 2, y + (cell_height - lunar_day_height) / 2 - 20),
                          str(day.day), fill=cell_color, font=font_small)  # 调整 day 的位置
                draw.text((x + (cell_width - desc_width) / 2, y + (cell_height - desc_height) / 2 + 20), day.desc,
                          fill=(0, 0, 0, 128), font=font_small)  # 调整 desc 的位置
        image.save("calendar2.png")
        return (pil2tensor(image.convert("RGBA")), )