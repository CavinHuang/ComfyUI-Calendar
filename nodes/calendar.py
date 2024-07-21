import matplotlib.pyplot as plt
import calendar
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from .util import pil2tensor
import glob
import os

NODE_NAME = 'Calendar'
# os.path.normpath(__file__)
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

print(default_font_dir)
print(FONT_LIST)
print(FONT_DICT)


class CalendarNode:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "year": ("STRING", {"default": "2021"}),
                "month": ("STRING", {"default": "1"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = 'calendarCreate'
    CATEGORY = '日历'

    def calendarCreate(self, year, month):

        year = 2024
        month = 7
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
        header_text = f"{calendar.month_name[month]} {year}"
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

        # 获取当月的日历
        cal = calendar.monthcalendar(year, month)

        # 绘制日历
        for week_index, week in enumerate(cal):
            for day_index, day in enumerate(week):
                if day != 0:
                    x = padding + day_index * cell_width
                    y = padding + header_height + cell_height + week_index * cell_height
                    day_bbox = draw.textbbox((0, 0), str(day), font=font_small)
                    day_width = day_bbox[2] - day_bbox[0]
                    draw.text((x + (cell_width - day_width) / 2, y), str(day), fill="black", font=font_small)

        # 保存图像
        image.save("calendar.png")
        return (pil2tensor(image.convert("RGB")), )