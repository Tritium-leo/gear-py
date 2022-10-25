import matplotlib.pyplot as plt

from pkg import str_2_img
from .setup_teardown import SetupTeardown


class TestStr2Img(SetupTeardown):
    def test_str_2_img(self):
        # data test
        data_list = [
            1,  # normal
            {"1": [2, 3]},  # dict,
            [1, 2, 3],  # list
            'xxx\nyyy\nzzz',  # multiline
        ]
        for data in data_list:
            img = str_2_img.str_2_img(data)
            plt.imshow(img)
            plt.pause(2)

        # align_test
        data = 'xxx\nyyyy\nzzz'

        for x_ in ['l', 'm', 'r']:
            for y_ in ['t', 'm', 'b']:
                img = str_2_img.str_2_img(data, align_x=x_, align_y=y_)
                plt.imshow(img)
                plt.pause(2)
