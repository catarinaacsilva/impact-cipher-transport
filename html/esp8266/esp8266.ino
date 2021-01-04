#include <Wire.h>
#include <ezTime.h>
#include <ESP8266WiFi.h>

#include <Curve25519.h>
#include <AES.h>
#include <CTR.h>

#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

#include "options.h"
#include "utils.h"

// assign the SPI bus to pins
#define BME_SCK D1
#define BME_MISO D4
#define BME_MOSI D2
#define BME_CS D3

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME280 bme(BME_CS, BME_MOSI, BME_MISO, BME_SCK); // software SPI

unsigned long delayTime, key_delay, cypher_delay;

uint8_t f[KEY_SIZE];
uint8_t k[KEY_SIZE];
uint8_t k_sensor[KEY_SIZE];
uint8_t key[SESSION_KEY_SIZE];
uint8_t iv[16];

Timezone Portugal;

// Send PubKey to Key Exchange service
void send_pubkey(uint8_t *key, int len) {
  // convert pubkey array to string
  char s_pubkey[(len * 2) + 1];
  Bytes2Hex(s_pubkey, key, len);

  // Prepare JSON document
  DynamicJsonDocument doc(128);
  doc["id"] = "sensor";
  doc["pubkey"] = s_pubkey;

  // Serialize JSON document
  String json;
  serializeJson(doc, json);

  // Register the public key
  HTTPClient http;
  http.begin(KEY_EXCHANGE_POST);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(json);
  http.end();
  while ((httpCode / 100) != 2) {
    delay(3000);
    http.begin(KEY_EXCHANGE_POST);
    http.addHeader("Content-Type", "application/json");
    httpCode = http.POST(json);
    http.end();
  }
}

// Request the client public key
void request_pubkey(uint8_t *out) {
  HTTPClient http;

  // Send request
  http.useHTTP10(true);
  http.begin(KEY_EXCHANGE_GET);
  int httpCode =  http.GET();

  // Try to read the foreign until there is no error
  while ((httpCode / 100) != 2) {
    // Disconnect
    http.end();
    delay(3000);
    http.begin(KEY_EXCHANGE_GET);
    httpCode =  http.GET();
  }

  // Parse response
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, http.getStream());

  // Read values
  Serial.println(doc["key"].as<String>());
  const char* key = doc["key"];
  Hex2Bytes(out, key, KEY_SIZE * 2);

  // Disconnect
  http.end();
}

// Uses the HTTP server to share the public keys and create a new session key
void init_session() {
  Serial.println("Init new session");
  // Generate the secret value "f" and the public value "k".
  unsigned long start = micros();
  Curve25519::dh1(k, f);
  unsigned duration1 = micros() - start;
  send_pubkey(k, KEY_SIZE);
  printHex("PubKey: ", k, KEY_SIZE);
  request_pubkey(k_sensor);
  printHex("Foreign PubKey: ", k_sensor , KEY_SIZE);
  start = micros();
  Curve25519::dh2(k_sensor, f);
  printHex("Shared Key", key , KEY_SIZE);
  memcpy(key, k_sensor, SESSION_KEY_SIZE);
  unsigned duration2 = micros() - start;
  printHex("Shared Session Key", key , SESSION_KEY_SIZE);
  key_delay = duration1 + duration2;
  Serial.println("Key Delay: " + key_delay);
}

void setup() {
  Serial.begin(115200);
  Serial.println(F("BME280 test"));

  // default settings
  // (you can also pass in a Wire library object like &Wire2)
  bool status = bme.begin();
  if (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1);
  }
  Serial.println("BME280 Test");
  delay(100);

  Serial.println("-- Default Test --");
  delayTime = 3000;

  // WiFi Connect
  WiFi.begin(SSID, PASSWORD);
  Serial.print("\n\r \n\rWorking to connect");

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("NodeMCU(ESP32)");
  Serial.print("Connected to ");
  Serial.println(SSID);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  setInterval(60);
  waitForSync();

  Portugal.setLocation("Europe/Lisbon");
  Serial.println("Portugal: " + Portugal.dateTime());
}

void generate_iv(byte  *iv, size_t size) {
  for (int i = 0 ; i < size ; i++ ) {
    iv[i] = (byte) getrnd();
  }
}

void send_data() {
  // Read BME280 values
  float t = bme.readTemperature();
  float h = bme.readHumidity();
  float p = bme.readPressure() / 100.0F;

  DynamicJsonDocument doc(256);
  doc["temperature"]   = t;
  doc["humidity"] = h;
  doc["pressure"] = p;

  char values[LENGTH];
  uint8_t input[LENGTH], output[LENGTH];
  memset(values, 0, sizeof(char)*LENGTH);
  memset(input, 0, sizeof(uint8_t)*LENGTH);
  memset(output, 0, sizeof(uint8_t)*LENGTH);
  serializeJson(doc, values, LENGTH);
  Serial.println(values);
  Char2Bytes(input, values , LENGTH);
  printHex("Input(HEX)", input, LENGTH);
  printBytes("Input(Bytes)", input, LENGTH);

  init_session();

  generate_iv(iv, 16);
  printHex("IV", iv, 16);

  unsigned long start = micros();
  CTR<AES128> ctr;
  ctr.setKey(key, SESSION_KEY_SIZE);
  ctr.setIV(iv, 16);
  ctr.setCounterSize(16);
  ctr.encrypt(output, input, LENGTH);
  cypher_delay = micros() - start;
  
  printHex("Output(HEX)", output, LENGTH);
  printBytes("Output(Bytes)", output, LENGTH);
  Serial.println("Cypher Delay: " + cypher_delay);
  Serial.println();

  char output_hex[(LENGTH * 2) + 1];
  Bytes2Hex(output_hex, output, LENGTH);

  char iv_hex[33];
  Bytes2Hex(iv_hex, iv, 16);

  DynamicJsonDocument reply(512);
  reply["cypher"] = output_hex;
  reply["iv"] = iv_hex;
  reply["key_delay"] = key_delay;
  reply["cypher_delay"] = cypher_delay;
  reply["time"] = Portugal.now();

  // Serialize JSON document
  String json;
  serializeJson(reply, json);
  
  // Register the public key
  HTTPClient http;
  http.begin(DATA_POST);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(json);
  http.end();
  while ((httpCode / 100) != 2) {
    delay(3000);
    http.begin(DATA_POST);
    http.addHeader("Content-Type", "application/json");
    httpCode = http.POST(json);
    http.end();
  }
}

void loop() {
  send_data();
  events();
  delay(delayTime);
}
