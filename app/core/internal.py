import io
import os
import random
import re
import string
from datetime import datetime, timedelta
from pathlib import Path

from pydantic.main import BaseModel
from wand.color import Color
from wand.image import Image
# from PIL import Image


def generate_random_string(len):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(len))

def extract_http_https_links(text):
    # 正则表达式匹配HTTP和HTTPS链接
    url_pattern = r'https?://[^\s"]+'
    links = re.findall(url_pattern, text)
    return links


def get_month_start_end(date: datetime):
    # 获取当月的第一天
    start_of_month = date.replace(day=1)

    # 获取下个月的第一天
    next_month = start_of_month + timedelta(days=31)
    start_of_next_month = next_month.replace(day=1)

    # 获取当月的最后一天
    end_of_month = start_of_next_month - timedelta(days=1)

    return start_of_month, end_of_month



def paginate_info(total_items, current_page, items_per_page):
    total_pages = (total_items + items_per_page - 1) // items_per_page
    is_first_page = current_page == 1
    is_last_page = current_page == total_pages
    has_previous_page = current_page > 1
    has_next_page = current_page < total_pages

    offsets = [-2, -1, 1, 2]
    candidate_pages = [current_page + offset for offset in offsets]
    valid_pages = [page for page in candidate_pages if 1 <= page <= total_pages]
    valid_pages.append(current_page)
    # valid_pages.sort()
    # if len(valid_pages) < 4:
    valid_pages.append(1)
    if total_pages != 0:
        valid_pages.append(total_pages)
    v_pages = [i for i in set(valid_pages)]
    v_pages.sort()

    print(v_pages)
    result = [v_pages[0]]
    for i in range(1, len(v_pages)):
        if v_pages[i] - v_pages[i - 1] > 1:
            result.append(-1)
            result.append(v_pages[i])
        else:
            result.append(v_pages[i])
    print({
        'current_page': current_page,
        'items_per_page': items_per_page,
        'total_pages': total_pages,
        'total_items': total_items,
        'is_first_page': is_first_page,
        'is_last_page': is_last_page,
        'has_previous_page': has_previous_page,
        'has_next_page': has_next_page,
        'adjacent_pages': result
    })
    return {
        'current_page': current_page,
        'items_per_page': items_per_page,
        'total_pages': total_pages,
        'total_items': total_items,
        'is_first_page': is_first_page,
        'is_last_page': is_last_page,
        'has_previous_page': has_previous_page,
        'has_next_page': has_next_page,
        'adjacent_pages': result
    }

class ImageProcessor:
    CONVERT_WEBP = 'image/convert,m_webp'
    # "image/convert,m_webp
    # option_str = "image/resize,m_fixed,h_100,w_100"
    # resize_options = ImageResizeOptions.from_string(option_str)
    def __init__(self, process_string: str):
        self.process_string = process_string
        self.operation = None
        self.params = {}
        self._parse_process_string()

    def _parse_process_string(self):
        # 确保字符串以 "image/" 开头
        if not self.process_string.startswith("image/"):
            raise ValueError("Invalid process string: must start with 'image/'")

        # 提取操作和参数部分
        operation_string = self.process_string[len("image/"):]
        operation_parts = operation_string.split(",")

        if not operation_parts:
            raise ValueError("Invalid process string: operation not found")

        # 第一个部分是操作
        self.operation = operation_parts[0]

        # 其余部分是参数
        for part in operation_parts[1:]:
            if "_" in part:
                key, value = part.split("_", 1)
                self.params[key] = value
            else:
                raise ValueError(f"Invalid parameter: {part}")

    def process(self, from_image, to_image) -> (str, bool):
        if self.operation == "convert":
            return self._convert(from_image, to_image)
        elif self.operation == "resize":
            pass
        else:
            raise ValueError(f"Unknown operation: {self.operation}")

    def _convert(self, from_image, to_image):
        if 'm' not in self.params or self.params['m'] != 'webp':
            raise ValueError("Unsupported convert operation or missing parameters")
        e = f"{to_image}webp/{Path(from_image).stem}.webp"
        os.makedirs(f"{to_image}webp/", exist_ok=True)
        if os.path.isfile(e):
            return e, True
        # with Image.open(from_image) as img:
        #     if img.mode == 'RGBA':
        #         img = img.convert('RGB')
        #     img.save(e, format="WEBP")
        # return e
        compress_to_target_size(from_image, e)
        return e, False


def compress_to_target_size(input_path, output_path, max_size_kb=20, initial_quality=95, step_quality=5, min_quality=10):
    with Image(filename=input_path) as img:
        # 初次转换为 WebP 格式
        img.format = 'webp'
        img.compression_quality = initial_quality
        img.save(filename=output_path)

        # 检查文件大小
        file_size_kb = os.path.getsize(output_path) / 1024
        print(f"Initial file size: {file_size_kb:.2f}KB")

        # 如果文件大小大于目标大小，开始逐步压缩
        while file_size_kb > max_size_kb and img.compression_quality > min_quality:
            img.compression_quality -= step_quality  # 降低质量
            img.resize(int(img.width * 0.9), int(img.height * 0.9))  # 缩小尺寸
            img.save(filename=output_path)
            file_size_kb = os.path.getsize(output_path) / 1024
            print(f"Adjusted file size: {file_size_kb:.2f}KB, Quality: {img.compression_quality}")

        # 最终检查
        if file_size_kb > max_size_kb:
            print(f"Warning: Unable to compress {input_path} to {max_size_kb}KB. Final size: {file_size_kb:.2f}KB")
        else:
            print(f"Success: Compressed {input_path} to {file_size_kb:.2f}KB")


def convert_long_to_str(obj):
    if isinstance(obj, dict):
        return {k: convert_long_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_long_to_str(item) for item in obj]
    elif isinstance(obj, int) and abs(obj) >= 2**53:  # 只转换 long 类型数字
        return str(obj)
    else:
        return obj

def gen_white_image():
    # 创建一个白色的图片（宽度 100 像素，高度 100 像素）
    img_io = io.BytesIO()
    with Image(width=100, height=100, background=Color('white')) as img:
        # 将图片保存到内存中
        img.format = 'png'  # 设置图片格式为 PNG
        img.save(file=img_io)
        img_io.seek(0)
    return img_io