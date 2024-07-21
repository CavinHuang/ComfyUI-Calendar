from datetime import datetime
from lunar_python import Lunar, LunarMonth
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from .util import pil2tensor
import glob
import os

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
        self.lunar_day = ''
        self.text = ''
        self.is_festival = False
        self.is_today = False
        self.is_jie = False
        self.is_qi = False

monthInGanZhi = ''

class CalendarLunarNode:
    """A node that displays a calendar with lunar dates."""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "year": ("INT", {"default": 2021, "min": 1900, "max": 2100}),
                "month": ("INT", {"default": 1, "min": 1, "max": 12}),
            },
        }
    
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = 'calendar_lunar'
    CATEGORY = '日历'

    def calendar_lunar(self, year, month):

        date_now = datetime.now()
        now = Lunar.fromYmd(year, month, date_now.day)

        state = {
            'year':year,
            'month': month,
            'year_in_chinese': '',
            'year_in_ganzhi': '',
            'year_shengxiao': '',
            'month_in_chinese': '',
            'month_in_ganzhi': '',
            'week_start': 0,
            'heads': ['日', '一', '二', '三', '四', '五', '六'],
            'days': []
        }

        self.render_state(state, now)

        print(state)

        return self.rend_canvas(state)

    def build_day(self, d: Lunar, state, now):
        global monthInGanZhi
        day = Day()
        lunarDay = d.getDayInChinese()
        if 1 == d.getDay():
            lunarDay = d.getMonthInChinese() + '月'

        gz = d.getMonthInGanZhi()
        if monthInGanZhi != '' and monthInGanZhi != gz:
            lunarDay = gz
        monthInGanZhi = gz
        day.lunar_day = lunarDay

        solar = d.getSolar()
        text = str(solar.getDay())
        if 1 == solar.getDay():
            text = str(solar.getMonth()) + '月'
        
        otherFestivals = d.getOtherFestivals()
        if len(otherFestivals) > 0:
            text = otherFestivals[0]
            day.is_festival = True

        festivals = d.getFestivals()
        if len(festivals) > 0:
            text = festivals[0]
            day.is_festival = True

        jq = d.getCurrentJieQi()
        if jq:
            text = jq.getName()
            day.isFestival = True
            day.isJie = jq.isJie()
            day.isQi = jq.isQi() 
        day.text = text
        if d.toString() == now.toString():
            day.is_today = True
        
        return day
    
    def render_state(self, state, now):
        month = LunarMonth.fromYm(state['year'], state['month'])
        size = month.getDayCount()
        days = []
        lunar = Lunar.fromYmd(state['year'], state['month'], 1)
        blankDay = Day()
        for _ in range(lunar.getWeek()):
            days.append(blankDay)

        days.append(self.build_day(lunar, state, now))
        lastWeek = 0
        for i in range(1, size):
            d = lunar.next(i)
            lastWeek = d.getWeek()
            days.append(self.build_day(d, state, now))

        for _ in range(6 - lastWeek):
            days.append(blankDay)

        state['days'] = days
        state['year_in_chinese'] = lunar.getYearInChinese()
        state['year_in_ganzhi'] = lunar.getYearInGanZhi()
        state['year_shengxiao'] = lunar.getYearShengXiao()
        state['month_in_chinese'] = lunar.getMonthInChinese()
        state['month_in_ganzhi'] = month.getGanZhi()


    def rend_canvas(self, state):
        cell_width = 100
        cell_height = 100
        padding = 20
        header_height = 100

         # 创建一个新的空白图像
        img_width = cell_width * 7 + padding * 2
        img_height = cell_height * 6 + padding * 2 + header_height
        image = Image.new('RGBA', size=(img_width, img_height), color=(255, 255, 255, 128))
        draw = ImageDraw.Draw(image)

        # 加载字体
        font_path = FONT_DICT[default_font]
        font = ImageFont.truetype(font_path, 36)
        font_small = ImageFont.truetype(font_path, 24)

        # 绘制表头
        header_text = f"{state['year']}年{state['month']}月 · {state['year_in_ganzhi']}年{state['month_in_chinese']}月"
        header_bbox = draw.textbbox((0, 0), header_text, font=font)
        header_width = header_bbox[2] - header_bbox[0]
        header_height_text = header_bbox[3] - header_bbox[1]
        draw.text(((img_width - header_width) / 2, padding), header_text, fill="black", font=font)

        # 绘制星期表头
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days_of_week):
            x = padding + i * cell_width
            y = padding + header_height
            day_bbox = draw.textbbox((0, 0), day, font=font_small)
            day_width = day_bbox[2] - day_bbox[0]
            draw.text((x + (cell_width - day_width) / 2, y), day, fill="black", font=font_small)

        # 按行绘制日历，把state['days']分成7列
        lines = []
        for i in range(0, len(state['days']), 7):
            lines.append(state['days'][i:i+7])

        # 绘制日历天
        for week_index, week in enumerate(lines):
            for day_index, day in enumerate(week):
                # x = padding + day_index * cell_width
                # y = padding + header_height + cell_height + week_index * cell_height
                # day_bbox = draw.textbbox((0, 0), day.text, font=font_small)
                # day_width = day_bbox[2] - day_bbox[0]
                # draw.text((x + (cell_width - day_width) / 2, y), day.lunar_day, fill="black", font=font_small)
                # draw.text((x + (cell_width - day_width) / 2, y + 30), day.text, fill="black", font=font_small)

                x = padding + day_index * cell_width
                y = padding + header_height + cell_height + week_index * cell_height
                
                lunar_day_bbox = draw.textbbox((0, 0), day.lunar_day, font=font_small)
                lunar_day_width = lunar_day_bbox[2] - lunar_day_bbox[0]
                lunar_day_height = lunar_day_bbox[3] - lunar_day_bbox[1]
                
                text_bbox = draw.textbbox((0, 0), day.text, font=font_small)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                draw.text((x + (cell_width - lunar_day_width) / 2, y + (cell_height / 2 + 10)), day.lunar_day, fill="black", font=font_small)

                draw.text((x + (cell_width - text_width) / 2, y + (cell_height / 2 - lunar_day_height - 10)), day.text, fill=(0, 0, 0, 128), font=font_small)


        image.save("calendar2.png")
        return (pil2tensor(image.convert("RGBA")), )