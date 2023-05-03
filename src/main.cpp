// Copyright 2023 sbchild

// Licensed under the Apache License, Version 2.0(the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

// http: // www.apache.org/licenses/LICENSE-2.0

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <SPI.h>
#include <U8g2lib.h>
#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

const char *ssid = "TP-LINK_6687";   // set your ssid
const char *password = "d123456789"; // set your password
WiFiUDP udp;
IPAddress staticIP(192, 168, 0, 123); // Set your desired static IP address
IPAddress gateway(192, 168, 0, 1);    // Set your gateway IP address
IPAddress subnet(255, 255, 255, 0);   // Set your subnet mask
IPAddress dns(8, 8, 8, 8);            // Set your primary DNS server

// change this define if needed
U8G2_MAX7219_32X8_F_4W_SW_SPI u8g2(U8G2_R2, 14, 13, 12, U8X8_PIN_NONE, U8X8_PIN_NONE);

void setup()
{
  Serial.begin(115200);
  u8g2.begin();
  u8g2.clearBuffer();
  u8g2.sendBuffer();
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    u8g2.clearBuffer();
    for (size_t i = 0; i < 32; i++)
    {
      uint8_t h = 4 + uint8_t(sin((millis() / 300.f) + float(i)) * 4.5);
      u8g2.drawPixel(i, h);
    }
    u8g2.sendBuffer();
    delay(100);
    Serial.println("Connecting to WiFi...");
  }
  WiFi.config(staticIP, gateway, subnet, dns);
  Serial.println("Connected to WiFi");
  u8g2.clearBuffer();
  u8g2.sendBuffer();
  udp.begin(1234);
}

void loop()
{
  int packetSize = udp.parsePacket();
  if (packetSize > 0)
  {
    uint8_t packetBuffer[packetSize];
    udp.read(packetBuffer, packetSize);
    if (packetSize != 32)
    {
      return;
    }
    u8g2.clearBuffer();
    for (int i = 0; i < packetSize; i++)
    {
      if (i < 16)
      {
        u8g2.drawPixel(15 - i, 7 - packetBuffer[i]);
      }
      else
      {
        u8g2.drawPixel(i, 7 - packetBuffer[i]);
      }
    }
    u8g2.sendBuffer();
  }
}
