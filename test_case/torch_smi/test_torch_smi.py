import threading
import time

from pkg import torch_smi
from .setup_teardown import SetupTeardown


class TestTorchSMI(SetupTeardown):
    def test_cuda_info(self):
        torch_smi.cuda_info('cuda:0')

    def test_get_gpu_thread(self):
        info = {}
        t = threading.Thread(target=torch_smi.get_gpu_thread, args=(0.1, info, 'cuda:0'), daemon=True)
        t.start()
        time.sleep(1)
        print(info)
        t._stop().set()
