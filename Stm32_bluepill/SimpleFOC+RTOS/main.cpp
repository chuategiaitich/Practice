#include <SimpleFOC.h>
#include <HardwareSerial.h>
#include <STM32FreeRTOS.h>

// ---------- Cảm biến và động cơ ----------
MagneticSensorSPI sensor = MagneticSensorSPI(PA4, 14, 0x3FFF);
BLDCMotor motor = BLDCMotor(11);
BLDCDriver3PWM driver = BLDCDriver3PWM(PB6, PB7, PB8, PB5);
HardwareSerial Serial3 = HardwareSerial(PB11, PB10);

// ---------- Biến toàn cục (dùng chung) ----------
float target_angle = 0;
float target_torque = 0;

// ---------- Task Handle ----------
TaskHandle_t MotorControlTaskHandle;
TaskHandle_t SerialReceiveTaskHandle;
TaskHandle_t DebugTaskHandle;

// ---------- Task 1: Motor Control ----------
void MotorControlTask(void *pvParameters) {
  for (;;) {
    motor.loopFOC();
    motor.PID_velocity.limit = target_torque;
    motor.move(target_angle);
    vTaskDelay(pdMS_TO_TICKS(1));
  }
}

// ---------- Task 2: Serial Receive ----------
void SerialReceiveTask(void *pvParameters) {
  for (;;) {
    if (Serial3.available()) {
      char c = Serial3.read();
      switch (c) {
        case 'a':
          target_angle = Serial3.parseFloat();
          break;
        case 't':
          target_torque = Serial3.parseFloat();
          break;
        default:
          break;
      }
    }
    vTaskDelay(pdMS_TO_TICKS(10));  // Giảm CPU load, đọc UART mỗi 10ms
  }
}

// ---------- Task 3: Debug Serial ----------
void DebugTask(void *pvParameters) {
  for (;;) {
    Serial.print(sensor.getAngle(), 4);
    Serial.print(" ; ");
    Serial.print(motor.current.d, 4);
    Serial.print(" | Stack [Motor,ReadSignal,Debug]: ");
    Serial.print(uxTaskGetStackHighWaterMark(MotorControlTaskHandle));
    Serial.print(", ");
    Serial.print(uxTaskGetStackHighWaterMark(SerialReceiveTaskHandle));
    Serial.print(", ");
    Serial.println(uxTaskGetStackHighWaterMark(DebugTaskHandle));
    vTaskDelay(pdMS_TO_TICKS(100)); // Gửi dữ liệu mỗi 100ms
  } 
}

// ---------- Setup ----------
void setup() {

  Serial.begin(115200);
  Serial3.begin(115200);

  // Cảm biến
  sensor.init();
  motor.linkSensor(&sensor);

  // Driver
  driver.voltage_power_supply = 12;
  driver.init();
  motor.linkDriver(&driver);

  // Cấu hình điều khiển
  motor.foc_modulation = FOCModulationType::SpaceVectorPWM;
  motor.controller = MotionControlType::angle;
  motor.PID_velocity.P = 0.2f;
  motor.PID_velocity.I = 20;
  motor.PID_velocity.limit = 3;  // moment tối đa mặc định (Nm)
  motor.voltage_limit = 6;
  motor.LPF_velocity.Tf = 0.01f;
  motor.P_angle.P = 20;
  motor.velocity_limit = 40;

  motor.init();
  motor.initFOC();

  // Tạo các task
  BaseType_t task;
  task = xTaskCreate(MotorControlTask, "MotorControl", 1024, NULL, configMAX_PRIORITIES - 1, &MotorControlTaskHandle); // FOC loop need  at least 
  if (task != pdPASS){Serial.println("Failed to create MotorControlTask");while (1);}
  task = xTaskCreate(SerialReceiveTask, "SerialReceive", 512, NULL, configMAX_PRIORITIES - 2, &SerialReceiveTaskHandle);
  if (task != pdPASS){Serial.println("Failed to create SerialReceiveTask");while (1);}
  task = xTaskCreate(DebugTask, "Debug", 512, NULL, 1, &DebugTaskHandle);
  if (task != pdPASS){Serial.println("Failed to create DebugTask");while (1);}
  vTaskStartScheduler();
}

void loop(){}
