# 项目演示

https://github.com/user-attachments/assets/79fe22a5-0589-43c9-9faa-3b553aafdcb0

if the video is empty, see this link: https://github.com/lykycy123/lerobot-piper/blob/main/W3_manipulator.mp4

# 项目硬件
使用PIPER松灵机械臂  
使用realsense摄像头，可以自定义个数  
使用手柄控制
# Install
Create a virtual environment with Python 3.10 and activate it, e.g. with [`miniconda`](https://docs.anaconda.com/free/miniconda/index.html):
```bash
conda create -y -n lerobot python=3.10
conda activate lerobot
```

Install 🤗 LeRobot:
```bash
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple

pip uninstall numpy
pip install numpy==1.26.0
pip install pynput
```

/!\ For Linux only, ffmpeg and opencv requires conda install for now. Run this exact sequence of commands:
```bash
conda install -c conda-forge ffmpeg
pip uninstall opencv-python
conda install "opencv>=4.10.0"
```

Install Piper:  
```bash
pip install python-can
pip install piper_sdk
sudo apt update && sudo apt install can-utils ethtool
pip install pygame
```

# piper集成lerobot
见lerobot_piper_tutorial/1. 🤗 LeRobot：新增机械臂的一般流程.pdf  
注意在使用的时候可能会出现ImportError: /lib/x86_64-linux-gnu/libstdc++.so.6: version `GLIBCXX_3.4.29' not found (required by /home/lyk/.conda/envs/lerobot/lib/python3.10/site-packages/cv2.cpython-310-x86_64-linux-gnu.so)的问题
```bash
conda install -c conda-forge libstdcxx-ng  # 安装或更新  

# 激活 Conda 环境后，设置 LD_LIBRARY_PATH  
conda activate lerobot  
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH  
# 激活can
cd piper_scripts/
bash can_activate.sh can0 1000000

# 验证是否生效  
echo $LD_LIBRARY_PATH  # 应包含 Conda 环境的 lib 目录

```

**注意在使用前需要包含训练好的模型**

# Teleoperate
```bash
python lerobot/scripts/control_robot.py \
    --robot.type=piper \
    --robot.inference_time=false \
    --control.type=teleoperate
```



# Record 
**注意所有的single_task名字不能重复，num_episodes是一个任务记录多少条数据，episode_time是一条数据的记录时间** \
Set dataset root path
```bash
HF_USER=$PWD/data
echo $HF_USER
```

```bash
python lerobot/scripts/control_robot.py \
    --robot.type=piper \
    --robot.inference_time=false \
    --control.type=record \
    --control.fps=30 \
    --control.single_task="move" \
    --control.repo_id=${HF_USER}/test \
    --control.num_episodes=2 \
    --control.warmup_time_s=2 \
    --control.episode_time_s=10 \
    --control.reset_time_s=10 \
    --control.play_sounds=true \
    --control.push_to_hub=false
```

Press right arrow -> at any time during episode recording to early stop and go to resetting. Same during resetting, to early stop and to go to the next episode recording.  
Press left arrow <- at any time during episode recording or resetting to early stop, cancel the current episode, and re-record it.  
Press escape ESC at any time during episode recording to end the session early and go straight to video encoding and dataset uploading.  

# visualize
```bash
python lerobot/scripts/visualize_dataset.py \
    --repo-id ${HF_USER}/test \
    --episode-index 0
```

# Replay
```bash
python lerobot/scripts/control_robot.py \
    --robot.type=piper \
    --robot.inference_time=false \
    --control.type=replay \
    --control.fps=30 \
    --control.repo_id=${HF_USER}/test \
    --control.episode=0
```

# Caution

1. In lerobots/common/datasets/video_utils, the vcodec is set to **libopenh264**, please find your vcodec by **ffmpeg -codecs**


# Train
具体的训练流程见lerobot_piper_tutorial/2. 🤗 AutoDL训练.pdf
```bash
python lerobot/scripts/train.py \
  --dataset.repo_id=${HF_USER}/jack \
  --policy.type=act \
  --output_dir=outputs/train/act_jack \
  --job_name=act_jack \
  --device=cuda \
  --wandb.enable=true
``` 


# Inference

注意，如果直接使用可能会出现缺少type字段的问题，在训练好的模型中，修改pretrained_model中config.json文件，在开头加上"type" : "act",

2025/6/13更新：新训练的模型，checkpoints配置文件中可能需要删除use_amp和device，如果报错raise ParsingError(f"Couldn't instantiate class {stringify_type(cls)} using the given arguments.") from e
draccus.utils.ParsingError: Couldn't instantiate class RecordControlConfig using the given arguments，则加上--control.device=cuda

HF_USER=$PWD/inference_real

还是使用control_robot.py中的record loop，配置 **--robot.inference_time=true** 可以将手柄移出。
```bash
python lerobot/scripts/control_robot.py \
    --robot.type=piper \
    --robot.inference_time=true \
    --control.type=record \
    --control.fps=30 \
    --control.single_task="move" \
    --control.repo_id=$USER/eval_act_jack \
    --control.num_episodes=1 \
    --control.warmup_time_s=2 \
    --control.episode_time_s=30 \
    --control.reset_time_s=10 \
    --control.push_to_hub=false \
    --control.policy.path=outputs/train/act_koch_pick_place_lego/checkpoints/latest/pretrained_model
```

**上述方法需要注意每次使用的命令行控制中control.single_task这部分名字不能重复，不方便经常使用，所以下述方法使用python代码控制,也方便集成和二次开发**
```bash
python lerobot/scripts/control_robot.py 
```
