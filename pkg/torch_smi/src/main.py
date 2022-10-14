import time
import warnings

import torch


def cuda_info(device) -> dict:
    """
    if in sub thread ,torch is shared
    :param device: e.q. cuda:0
    :return:
    """
    res = {}
    memory_reserved = torch.cuda.memory_reserved(device)
    max_memory_reserved = torch.cuda.max_memory_reserved(device)
    memory_allocated = torch.cuda.memory_allocated(device)
    max_memory_allocated = torch.cuda.max_memory_allocated(device)

    res.update({
        "memory_reserved": memory_reserved,
        "max_memory_reserved": max_memory_reserved,
        "memory_allocated": memory_allocated,
        "max_memory_allocated": max_memory_allocated,
    })
    return res


def get_gpu_process(sec: float = 0.1, info: dict = {}, device: str = 'cuda:0') -> None:
    """
    :param sec: how long to get info
    :return:
    """
    # TODO process share torch module
    warnings.warn("it's a todo function, not solute process share torch module yet")
    while True:
        time.sleep(sec)
        info[round(time.time(), 2)] = cuda_info(device, None)
        # TODO LOG_IN_MEMORY_MAX_LIMIT TO DUMP FILE
        # if sys.getsizeof(info) > 500*1024*1024:


def get_gpu_thread(sec: float = 0.1, info: dict = {}, device: str = 'cuda:0') -> None:
    """
    running in thread to log cuda info
    WARNING:info not MAX_LIMIT ,it maybe grew up too big

    :param sec: sec to get cuda info
    :param info: return data
    :param device: e.q. cuda:0
    :return:
    """
    while True:
        time.sleep(sec)
        info[round(time.time(), 2)] = cuda_info(device, torch)
        # TODO LOG_IN_MEMORY_MAX_LIMIT TO DUMP FILE
        # if sys.getsizeof(info) > 500*1024*1024:
