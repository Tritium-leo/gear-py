import time
from collections import defaultdict

from pynvml import *


def nvidia_info() -> dict:
    # pip install nvidia-ml-py
    nvidia_dict = {
        "state": True,
        "nvidia_version": "",
        "nvidia_count": 0,
        "gpus": []
    }
    try:
        nvmlInit()
        nvidia_dict["nvidia_version"] = nvmlSystemGetDriverVersion()
        nvidia_dict["nvidia_count"] = nvmlDeviceGetCount()
        for i in range(nvidia_dict["nvidia_count"]):
            handle = nvmlDeviceGetHandleByIndex(i)
            memory_info = nvmlDeviceGetMemoryInfo(handle)
            procinfo = nvmlDeviceGetComputeRunningProcesses(handle)

            proc_name_dict = {}
            proc_info = {}
            for proc in procinfo:
                pid = proc.pid
                process_name = nvmlSystemGetProcessName(pid)
                proc_info[pid] = proc.__dict__
                proc_name_dict[pid] = process_name

            gpu = {
                "gpu_name": nvmlDeviceGetName(handle),
                "total": memory_info.total,
                "free": memory_info.free,
                "used": memory_info.used,
                "temperature": f"{nvmlDeviceGetTemperature(handle, 0)}℃",
                "powerStatus": nvmlDeviceGetPowerState(handle),
                "proc_name_dict": proc_name_dict,
                "proc_info": proc_info,  # process use memory
            }
            nvidia_dict['gpus'].append(gpu)
    except NVMLError as _:
        nvidia_dict["state"] = False
    except Exception as _:
        nvidia_dict["state"] = False
    finally:
        try:
            nvmlShutdown()
        except:
            pass
    return nvidia_dict


def get_gpu_process(sec: float = 0.1, info: dict = {}) -> None:
    """
    :param sec: how long to get info
    :return:
    """
    while True:
        time.sleep(sec)
        info[round(time.time(), 2)] = nvidia_info()
        # TODO LOG_IN_MEMORY_MAX_LIMIT TO DUMP FILE
        # if sys.getsizeof(info) > 500*1024*1024:


def trans_2_process_info(drive: str, time_info: dict) -> dict:
    # {
    #     "state": True,
    #     "nvidia_version": "",
    #     "nvidia_count": 0,
    #     "gpus": [{"gpu_name": nvmlDeviceGetName(handle),
    #               "total": memory_info.total,
    #               "free": memory_info.free,
    #               "used": memory_info.used,
    #               "temperature": f"{nvmlDeviceGetTemperature(handle, 0)}℃",
    #               "powerStatus": nvmlDeviceGetPowerState(handle),
    #               "proc_name_dict": proc_name_dict,
    #               "proc_info": {pid:{'usedGpuMemory':int,"gpuInstanceId":int,"computeInstanceId":int}},  # process use memory
    #               }, ...]
    # }

    res = defaultdict(dict)  # {pid:{time:{"in_all_gpu":{},"single_gpu":{},}}
    for p_time, info in time_info.items():

        for gpu in info['gpus']:
            proc_info = gpu['proc_info']
            for pid, info in proc_info.items():
                if pid not in res:
                    res[pid] = defaultdict(dict)
                pres = res[pid][p_time]
                gpu_memory = info.get('usedGpuMemory', None)
                if isinstance(gpu_memory, (int, float)):
                    gpu_memory = round(gpu_memory / 1024 / 1024, 2)
                if pid not in pres:
                    pres['single_gpu'] = defaultdict(dict)
                    pres['in_all_gpu'] = defaultdict(dict)
                pres['single_gpu'][f"[{drive}]{gpu['gpu_name']}"] = {"usedGpuMemory": gpu_memory}

                prev_use = pres.get('usedGpuMemory', None)  # None int
                add_use = gpu_memory  # None int
                if prev_use is None and add_use is None:
                    add_res = None
                elif prev_use is None or add_use is None:
                    add_res = prev_use if prev_use is not None else add_use
                else:
                    add_res = prev_use + add_use
                pres['in_all_gpu'] = {"usedGpuMemory": add_res}
    return res
