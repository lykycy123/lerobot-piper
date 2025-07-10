from lerobot.common.policies.act.modeling_act import ACTPolicy
from lerobot.common.robot_devices.robots.configs import PiperRobotConfig
from lerobot.common.robot_devices.robots.piper import PiperRobot
from lerobot.common.robot_devices.utils import busy_wait
from lerobot.common.robot_devices.control_utils import log_control_info
import time
import torch
import cv2


inference_time_s = 30

fps = 30
device = "cuda"  # TODO: On Mac, use "mps" or "cpu"

# 加载训练后policy
# ckpt_path = "outputs/train/act_koch_test/checkpoints/last/pretrained_model"
ckpt_path = "outputs/train/W3_act/checkpoints/060000/pretrained_model"

policy = ACTPolicy.from_pretrained(ckpt_path)
policy.to(device)

robot = PiperRobot(PiperRobotConfig(inference_time = inference_time_s))
robot.connect()

for _ in range(inference_time_s * fps):
    start_time = time.perf_counter()

    # Read the follower state and access the frames from the cameras
    observation = robot.capture_observation()

    # Convert to pytorch format: channel first and float32 in [0,1]
    # with batch dimension
    for name in observation:
        if "image" in name:
            observation[name] = observation[name].type(torch.float32) / 255
            observation[name] = observation[name].permute(2, 0, 1).contiguous()

        observation[name] = observation[name].unsqueeze(0)
        observation[name] = observation[name].to(device)

        # 图像显示（闪现，有问题）
        image_keys = [key for key in observation if "image" in key]
        for key in image_keys:
            cv2.imshow(key, cv2.cvtColor(observation[key].cpu().numpy(), cv2.COLOR_RGB2BGR))
        cv2.waitKey(1)




    # Compute the next action with the policy
    # based on the current observation
    action = policy.select_action(observation)
    # Remove batch dimension
    action = action.squeeze(0)
    # Move to cpu, if not already the case
    action = action.to("cpu")
    # Order the robot to move
    robot.send_action(action)

    dt_s = time.perf_counter() - start_time
    busy_wait(1 / fps - dt_s)

    log_control_info(robot, dt_s, fps=fps)


robot.__del__()