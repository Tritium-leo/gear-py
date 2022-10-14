import multiprocessing
import time

from pkg import nvidia_smi
from .setup_teardown import SetupTeardown


class TestNvidiaSMI(SetupTeardown):
    def test_nvidia_info(self):
        res = nvidia_smi.nvidia_info()
        self.assertIs(type(res), dict)

    def test_get_gpu_process(self):
        info = multiprocessing.Manager().dict()
        p = multiprocessing.Process(target=nvidia_smi.get_gpu_process, args=(0.1, info))
        p.start()
        try:
            time.sleep(0.5)
        finally:
            p.terminate()
        print(dict(info))
        self.assertIs(type(dict(info)), dict)

    def test_trans_2_process_info(self):
        # should prefix run a torch task to set tensor in GPU
        info = multiprocessing.Manager().dict()
        p = multiprocessing.Process(target=nvidia_smi.get_gpu_process, args=(0.1, info))
        p.start()
        try:
            time.sleep(1)
        finally:
            p.terminate()
        res = nvidia_smi.trans_2_process_info('cuda:0', dict(info))
        print(res)
