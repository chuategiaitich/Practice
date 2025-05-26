import odrive
from odrive.enums import *
import time
import math
import odrive.legacy_config
from odrive.enums import AxisState
from odrive.utils import request_state

odrv0 = None

def connect_odrive():
    global odrv0
    print("Searching for an ODrive...")
    odrv0 = odrive.find_any()
    print(f"ODrive connected! Firmware: {odrv0.fw_version_major}.{odrv0.fw_version_minor}.{odrv0.fw_version_revision}")
    return odrv0

def calibration():
    global odrv0
    odrv = odrv0
    if odrv is None:
        print("Disconnected. Run connect_odrive().")
        return

    #Erase old config
    print("Erasing old config and rebooting...")
    odrv.erase_configuration()
    odrv.reboot()
    time.sleep(5)
    odrv0 = odrive.find_any()
    print("Done.")
    print("Starting configuration...")

    #Power
    odrv.config.dc_bus_overvoltage_trip_level = 12
    odrv.config.dc_bus_undervoltage_trip_level = 10.5
    odrv.config.dc_max_positive_current = 5
    odrv.config.dc_max_negative_current = -math.inf
    odrv.config.brake_resistor0.enable = True
    odrv.config.brake_resistor0.resistance = 2

    #Motor
    odrv.axis0.config.motor.motor_type = MotorType.HIGH_CURRENT
    odrv.axis0.config.motor.pole_pairs = 20
    odrv.axis0.config.motor.torque_constant = 0.09188888888888888
    odrv.axis0.config.motor.current_soft_max = 5
    odrv.axis0.config.motor.current_hard_max = 16.5
    odrv.axis0.config.motor.calibration_current = 2
    odrv.axis0.config.motor.resistance_calib_max_voltage = 5
    odrv.axis0.config.calibration_lockin.current = 2
    odrv.axis0.motor.motor_thermistor.config.enabled = False

    #Encoder
    odrv.axis0.config.load_encoder = EncoderId.ONBOARD_ENCODER0
    odrv.axis0.config.commutation_encoder = EncoderId.ONBOARD_ENCODER0

    #Controller
    odrv.axis0.controller.config.control_mode = ControlMode.VELOCITY_CONTROL
    odrv.axis0.controller.config.input_mode = InputMode.VEL_RAMP
    odrv.axis0.controller.config.vel_limit = 10
    odrv.axis0.controller.config.vel_limit_tolerance = 1.2
    odrv.axis0.config.torque_soft_min = -math.inf
    odrv.axis0.config.torque_soft_max = math.inf
    odrv.axis0.trap_traj.config.accel_limit = 10
    odrv.axis0.controller.config.vel_ramp_rate = 10
    odrv.can.config.protocol = Protocol.NONE
    odrv.axis0.config.enable_watchdog = False
    odrv.config.enable_uart_a = False

    #Saved
    print("Saving configuration...")
    odrv.save_configuration()
    print("Done.")
    print("Rebooting ODrive...")
    odrv.reboot()
    time.sleep(5)
    odrv = odrive.find_any()
    print("ODrive Ready.")

    #Calibration
    print("Running calibration...")
    odrv.axis0.requested_state = AxisState.FULL_CALIBRATION_SEQUENCE
    while odrv.axis0.current_state != AxisState.IDLE:
        time.sleep(0.1)
    print("Done.")
    print("Motor is now IDLE")
    odrv.axis0.requested_state = AxisState.FULL_CALIBRATION_SEQUENCE

def print_encoder_position(duration):
    global odrv0
    if odrv0 is None:
        print("Disconnected. Run connect_odrive().")
        return
    print("Reading encoder raw value:")
    start_time = time.time()
    while time.time() - start_time < duration:  #seccond
        try:
            encoder_raw_value = odrv0.onboard_encoder0.raw
            # print(f"Raw Encoder Value (Axis 0): {encoder_raw_value}")
            print(f"{time.time() - start_time:.2f}s - Raw Value: {encoder_raw_value}")
        except AttributeError:
            print("Lỗi: Cant access encoder. Make sure Axis 0 calibrated.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    try:
        connect_odrive()
        # calibration()
        print_encoder_position(15)
    except odrive.exceptions.ODriveError as e:
        print(f"ODrive error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")