#include "WiFi.h"
#include <WebSocketsClient.h>
#include <MPU9250_WE.h>
#include <Wire.h>
#define MPU9250_ADDR 0x68

MPU9250_WE myMPU9250 = MPU9250_WE(MPU9250_ADDR);
// const char* ssid = "NCAIR IOT";
// const char* password = "Asim@123Tewari";
const char* ssid = "Zwilling_Labs";
const char* password = "will@1234";
// const char* ws_host = "192.168.0.103";
// const int ws_port = 8080;
// const char* ws_path = "/";
const char* ws_host = "twin.zwillinglabs.io";
const int ws_port = 443;
const char* ws_path = "/api/iot/data";

WebSocketsClient webSocket;

bool websocket_flag = true;
bool isConnected = false;

// Define a structure to hold the data
struct SensorData {
  float ax;
  float ay;
  float az;
  float gx;
  float gy;
  float gz;
  int cps;
  String sensor_id;
};

QueueHandle_t uartQueue = NULL;
TaskHandle_t readUARTTask_h = NULL;
TaskHandle_t sendWebSocketTask_h = NULL;

void readUARTTask(void* parameter) {
  for (;;) {
  xyzFloat accel = myMPU9250.getGValues();
  xyzFloat gyro = myMPU9250.getGyrValues();

    // Fill the structure with data
    SensorData data;
    data.ax = accel.x;
    data.ay = accel.y;
    data.az = accel.z;
    data.gx = gyro.x;
    data.gy = gyro.y;
    data.gz = gyro.z;
    data.cps = 1;             
    data.sensor_id = "95";

    // Serial.println(data);
  // Serial.println("Acceleration in g (x,y,z):");
  // Serial.print(gValue.x);
  // Serial.print("   ");
  // Serial.print(gValue.y);
  // Serial.print("   ");
  // Serial.println(gValue.z);
  // Serial.print("Resultant g: ");
  // Serial.println(resultantG);

  // Serial.println("Gyroscope data in degrees/s: ");
  // Serial.print(gyr.x);
  // Serial.print("   ");
  // Serial.print(gyr.y);
  // Serial.print("   ");
  // Serial.println(gyr.z);
  xQueueSend(uartQueue, &data, portMAX_DELAY);
  delay(1000);
  }
}

void sendWebSocketTask(void* parameter) {
  SensorData data;
  for (;;) {
    if (xQueueReceive(uartQueue, &data, portMAX_DELAY)) {
      checkWifi();  // Tries to reconnect to WiFi in Case of disconnect

      if (isConnected) {
        // Create JSON payload with required structure
        String jsonData = "{";
        jsonData += "\"mac_address\":\"00:1A:2B:3C:4D:5E\",";
        jsonData += "\"data\":{\"vibration\":[{";
        jsonData += "\"ax\":" + String(data.ax, 2) + ",";
        jsonData += "\"ay\":" + String(data.ay, 2) + ",";
        jsonData += "\"az\":" + String(data.az, 2) + ",";
        jsonData += "\"gx\":" + String(data.gx, 2) + ",";
        jsonData += "\"gy\":" + String(data.gy, 2) + ",";
        jsonData += "\"gz\":" + String(data.gz, 2) + ",";
        jsonData += "\"cps\":" + String(data.cps) + ",";
        jsonData += "\"sensor_id\":\"" + data.sensor_id + "\"";
        jsonData += "}]}";
        jsonData += "}";

        Serial.println(jsonData);
        webSocket.sendTXT(jsonData);
      // websocket_flag = true;
      // while (websocket_flag) {
      //   webSocket.loop();
      //   if (isConnected) {
      //     webSocket.sendTXT(value);
      //     // Serial.print(uartData);
      //     websocket_flag = false;
      //   }
      // }
      }
    }
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  if(!myMPU9250.init()){
    Serial.println("MPU9250 does not respond");
  }
  else{
    Serial.println("MPU9250 is connected");
  }

  init_wifi(); // Initialize WiFi connection
  
  // Serial.println("Position you MPU9250 flat and don't move it - calibrating...");
  // delay(1000);
  myMPU9250.autoOffsets();
  // Serial.println("Done!");
  myMPU9250.enableGyrDLPF();
  myMPU9250.setGyrDLPF(MPU9250_DLPF_6);
  myMPU9250.setSampleRateDivider(5);
  myMPU9250.setGyrRange(MPU9250_GYRO_RANGE_250);
  myMPU9250.setAccRange(MPU9250_ACC_RANGE_2G);
  myMPU9250.enableAccDLPF(true);
  myMPU9250.setAccDLPF(MPU9250_DLPF_6);
  myMPU9250.setMagOpMode(AK8963_CONT_MODE_100HZ);
  // delay(200);

  // Queue for sending data between tasks
  uartQueue = xQueueCreate(10, sizeof(SensorData));
  if (uartQueue == nullptr) Serial.println("Queue Failed to be created");

  xTaskCreatePinnedToCore(
    readUARTTask,     // Function to be called
    "Read UART",      // Name of the task
    4096,             // Stack size (bytes)
    NULL,             // Parameter to pass
    1,                // Task priority
    &readUARTTask_h,  // Task handle
    0                 // Run on core 0
  );

  xTaskCreatePinnedToCore(
    sendWebSocketTask,     // Function to be called
    "Send WebSocket",      // Name of the task
    4096,                  // Stack size (bytes)
    NULL,                  // Parameter to pass
    1,                     // Task priority
    &sendWebSocketTask_h,  // Task handle
    1                      // Run on core 1
  );
}

void loop() {
  // Empty loop
  delay(1000);
}

void init_wifi() {
  WiFi.mode(WIFI_STA);
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print("."); // Print dots while waiting to connect
  }
  Serial.println("\nWiFi connected");
}

void checkWifi() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, attempting to reconnect...");
    WiFi.reconnect();
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print("."); // Print dots while reconnecting
    }
    Serial.println("\nWiFi reconnected");
    webSocket.begin(ws_host, ws_port, ws_path);
  }
}

void webSocketEvent(WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      websocket_flag = false;
      isConnected = false;
      break;
    case WStype_CONNECTED:
      Serial.printf("[WSc] Connected to url: %s\n", payload);
      isConnected = true;
      break;
    case WStype_TEXT:
      Serial.printf("[WSc] get text: %s\n", payload);
      break;
    case WStype_BIN:
      Serial.printf("[WSc] get binary length: %u\n", length);
      break;
    default:
      break;
  }
}







