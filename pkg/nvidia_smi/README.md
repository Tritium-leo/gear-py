# This tool can get nvidia info(content process used) like

## 可以获得进程级别的显存占用(can get process used gpu memory info)

```json
{
  "state": true,
  "nvidia_version": "",
  "nvidia_count": 0,
  "gpus": [
    {
      "gpu_name": "Geforce 2060 6GB",
      "total": "6GB",
      "free": "4GB",
      "used": "2GB",
      "temperature": "42℃",
      "powerStatus": 2,
      "proc_name_dict": {
        "8465": "XXX/xxx_pytorch/venv/bin/python3"
      },
      "proc_info": {
        "8465": {
          "usedGpuMemory": "2GB",
          "gpuInstanceId": "4GB",
          "computeInstanceId": "2GB"
        }
      }
    }
  ]
}
```


## it's also can run in subprocess
use function
```python 
import multiprocessing
info = multiprocessing.Manager().dict()
p = multiprocessing.Process(target=get_gpu_process, args=(0.1, info))
p.start()
try:
    ...
finally:
    p.terminate()
```

A simple trans_info_func
```python
import multiprocessing
info = multiprocessing.Manager().dict()
p = multiprocessing.Process(target=get_gpu_process, args=(0.1, info))
p.start()
try:
    device = 'cuda:0'
    ...
    res = trans_2_process_info(device,dict(info))
    # {pid:{time:{"in_all_gpu":{},"single_gpu":{},}} (MB)
    # e.q. 
    """
    {
      "1665723083.88": {
        "single_gpu": {
          "[cuda:1]NVIDIA RTX A6000": {
            "usedGpuMemory": 17.0
          }
        },
        "in_all_gpu": {
          "usedGpuMemory": 17.0
        }
      },
      "1665723083.99": {
        "single_gpu": {
          "[cuda:1]NVIDIA RTX A6000": {
            "usedGpuMemory": 281.0
          }
        },
        "in_all_gpu": {
          "usedGpuMemory": 281.0
        }
      },
    }
    """
finally:
    p.terminate()
```