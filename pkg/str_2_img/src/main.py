import json
from functools import reduce
from typing import Any

import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont


def str_2_img(data: Any, align_x: str = 'left', align_y: str = 'top') -> Image.Image:
    """
    Use PIL , trans str to img obj
    Supported choose align style
    Args:
        data: Any will be trans to str,supported(json dump)
        align_x: enum[’l', 'm', 'r']
        align_y: enum['t', 'm', 'b']

    Returns:
        Image.Image
    """
    # validater
    align_x_map = {"l": ['left', 'l', 'L'], 'm': ['middle', 'm', 'M'], "r": ['right', 'r', 'R']}
    align_y_map = {"t": ['top', 't', 'T'], "m": ['middle', 'm', 'M'], 'b': ['bottom', 'b', 'B']}
    align_x = [one for one, chooses in align_x_map.items() if align_x in chooses]
    align_y = [one for one, chooses in align_y_map.items() if align_y in chooses]
    assert len(align_x) > 0
    assert len(align_y) > 0
    align_x, align_y = align_x[0], align_y[0]

    if isinstance(data, (dict, list)):
        data = json.dumps(data, ensure_ascii=False, indent=2)
    else:
        data = str(data)
    assert isinstance(data, str)

    # core
    data_list = data.split('\n')

    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    fontText = ImageFont.truetype('font/simsun.ttc', 500, encoding='utf-8')

    max_len_data = reduce(lambda x, y: x if len(x) > len(y) else y, data_list)  # 最长的文本
    data_width = round(fontText.getlength(max_len_data))  # 最大宽度
    line_height = fontText.getbbox(max_len_data)[3]  # bottom - top 每行的高度
    data_len = len(data_list)  # 行深
    data_height = line_height * data_len  # 最大高度

    img_width, img_height = data_width, data_height  # 生成图片的 宽高
    img = Image.new(mode='RGB', size=(img_width * 3, img_height * 3), color=(255, 255, 255))  # 放大生成后压缩回原尺寸，来生成高分辨率图片
    draw = ImageDraw.Draw(img, mode='RGB')
    for idx, one in enumerate(data_list):
        if not one:
            continue
        # 对齐方式
        if align_x == 'l':
            x_s = 0
        elif align_x == 'm':
            line_width = fontText.getlength(one)
            whole_line_width = img.size[0]
            x_s = (whole_line_width - line_width) // 2
        elif align_x == 'r':
            line_width = fontText.getsize(one)[0]
            whole_line_width = img.size[0]
            x_s = whole_line_width - line_width
        else:
            raise ValueError(f"unsupported align_x,{align_x}")
        if align_y == 't':
            y_s = idx * line_height
        elif align_y == 'm':
            whole_height = img.size[1]
            y_s = ((whole_height - data_height) // 2) + idx * line_height
        elif align_y == 'b':
            whole_height = img.size[1]
            y_s = (whole_height - data_height) + idx * line_height
        else:
            raise ValueError(f"unsupported align_y,{align_y}")

        draw.text((x_s, y_s), one, 'black', font=fontText)  # 绘制文字
    img = img.resize((img_width, img_height))

    return img
