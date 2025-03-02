import pygame
import threading
import time
from typing import Dict

class SixAxisArmController:
    def __init__(self):
        # 初始化pygame和手柄
        pygame.init()
        pygame.joystick.init()
        
        # 检查是否有连接的手柄
        if pygame.joystick.get_count() == 0:
            raise Exception("未检测到手柄")
        
        # 初始化手柄
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        
        # 初始化关节和夹爪状态
        self.joints = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 6个关节
        self.gripper = 0.0  # 夹爪状态
        self.speeds = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 6个关节的速度
        self.gripper_speed = 0.0  # 夹爪速度
        
        # 定义关节弧度限制（计算好的范围）
        self.joint_limits = [
            (-92000 / 57324.840764, 92000 / 57324.840764),  # joint1
            (-1300 / 57324.840764, 90000 / 57324.840764),   # joint2
            (-80000 / 57324.840764, 0 / 57324.840764),   # joint3
            (-90000 / 57324.840764, 90000 / 57324.840764),  # joint4
            (-77000 / 57324.840764, 19000 / 57324.840764),  # joint5
            (-90000 / 57324.840764, 90000 / 57324.840764)   # joint6
        ]

        # 启动更新线程
        self.running = True
        self.thread = threading.Thread(target=self.update_joints)
        self.thread.start()
    
    def update_joints(self):
        while self.running:
            # 处理事件队列
            try:
                pygame.event.pump()
            except Exception as e:
                self.stop()
                continue
                
            # 获取摇杆和按钮输入
            left_x = -self.joystick.get_axis(0)  # 左摇杆x轴
            if abs(left_x) < 0.5:
                left_x = 0.0

            left_y = -self.joystick.get_axis(1)  # 左摇杆y轴（取反，因为y轴向下为正
            if abs(left_y) < 0.5:
                left_y = 0.0

            right_x = -self.joystick.get_axis(3)  # 右摇杆x轴（取反，因为y轴向下为正）
            if abs(right_x) < 0.5:
                right_x = 0.0
            
            # 获取方向键输入
            hat = self.joystick.get_hat(0)
            up = hat[1] == 1
            down = hat[1] == -1
            left = hat[0] == -1
            right = hat[0] == 1
            
            # 获取按钮输入
            circle = self.joystick.get_button(1)  # 圈按钮
            cross = self.joystick.get_button(0)  # 叉按钮
            triangle = self.joystick.get_button(2)
            square = self.joystick.get_button(3)
            
            # 映射输入到速度
            self.speeds[0] = left_x * 0.01  # joint1速度
            self.speeds[1] = left_y * 0.01  # joint2速度
            self.speeds[2] = 0.01 if triangle else (-0.01 if square else 0.0)  # joint3速度
            self.speeds[3] = right_x * 0.01  # joint4速度
            self.speeds[4] = 0.01 if up else (-0.01 if down else 0.0)  # joint5速度
            self.speeds[5] = 0.01 if right else (-0.01 if left else 0.0)  # joint6速度
            self.gripper_speed = 0.01 if circle else (-0.01 if cross else 0.0)  # 夹爪速度
            
            # 积分速度到关节位置
            for i in range(6):
                self.joints[i] += self.speeds[i]
            self.gripper += self.gripper_speed
            
            # 关节范围保护
            for i in range(6):
                min_val, max_val = self.joint_limits[i]
                self.joints[i] = max(min_val, min(max_val, self.joints[i]))
            
            # 夹爪范围保护（0~0.08弧度）
            self.gripper = max(0.0, min(0.08, self.gripper))
            
            # 控制更新频率
            time.sleep(0.02)
    
    def get_action(self) -> Dict:
        # 返回机械臂的当前状态
        return {
            'joint0': self.joints[0],
            'joint1': self.joints[1],
            'joint2': self.joints[2],
            'joint3': self.joints[3],
            'joint4': self.joints[4],
            'joint5': self.joints[5],
            'gripper': self.gripper
        }
    
    def stop(self):
        # 停止更新线程
        self.running = False
        self.thread.join()
        pygame.quit()
        print("Gamepad exits")

    def reset(self):
        self.joints = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 6个关节
        self.gripper = 0.0  # 夹爪状态
        self.speeds = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 6个关节的速度
        self.gripper_speed = 0.0  # 夹爪速度

# 使用示例
if __name__ == "__main__":
    arm_controller = SixAxisArmController()
    try:
        while True:
            print(arm_controller.get_action())
            time.sleep(0.1)
    except KeyboardInterrupt:
        arm_controller.stop()