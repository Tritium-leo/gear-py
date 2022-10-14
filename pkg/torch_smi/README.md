Like nvidia_smi
This is a log_gpu_memory_cost_info in cuda by pytorch

- cuda_info(device,torch_ins)

```python
import torch

res = cuda_info('cuda:0')

{
    "memory_reserved": 46137344,
    "max_memory_reserved": 46137344,
    "memory_allocated": 41642496,
    "max_memory_allocated": 42843648
}
```

- get_gpu_thread(sec,info,device,)

```python
import threading

info = {}
t = threading.Thread(target=get_gpu_thread, args=(0.1, info, 'cuda:0'), daemon=True)
t.start()
```