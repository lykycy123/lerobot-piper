from typing import Protocol

from lerobot.common.robot_devices.motors.configs import (
    DynamixelMotorsBusConfig,
    FeetechMotorsBusConfig,
    PiperMotorsBusConfig,
    MotorsBusConfig
)


class MotorsBus(Protocol):
    def motor_names(self): ...
    def set_calibration(self): ...
    def apply_calibration(self): ...
    def revert_calibration(self): ...
    def read(self): ...
    def write(self): ...


def make_motors_buses_from_configs(motors_bus_configs: dict[str, MotorsBusConfig]) -> list[MotorsBus]:
    motors_buses = {}

    for key, cfg in motors_bus_configs.items():
        if cfg.type == "dynamixel":
            from lerobot.common.robot_devices.motors.dynamixel import DynamixelMotorsBus

            motors_buses[key] = DynamixelMotorsBus(cfg)

        elif cfg.type == "feetech":
            from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus

            motors_buses[key] = FeetechMotorsBus(cfg)

        elif cfg.type == "piper":
            from lerobot.common.robot_devices.motors.piper import PiperMotorsBus

            motors_buses[key] = PiperMotorsBus(cfg)

        else:
            raise ValueError(f"The motor type '{cfg.type}' is not valid.")

    return motors_buses


def make_motors_bus(motor_type: str, **kwargs) -> MotorsBus:
    if motor_type == "dynamixel":
        from lerobot.common.robot_devices.motors.dynamixel import DynamixelMotorsBus

        config = DynamixelMotorsBusConfig(**kwargs)
        return DynamixelMotorsBus(config)

    elif motor_type == "feetech":
        from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus

        config = FeetechMotorsBusConfig(**kwargs)
        return FeetechMotorsBus(config)
    
    elif motor_type == "piper":
        from lerobot.common.robot_devices.motors.piper import PiperMotorsBus

        config = PiperMotorsBusConfig(**kwargs)
        return PiperMotorsBus(config)

    else:
        raise ValueError(f"The motor type '{motor_type}' is not valid.")

def get_motor_names(arm: dict[str, MotorsBus]) -> list:
        return [f"{arm}_{motor}" for arm, bus in arm.items() for motor in bus.motors]