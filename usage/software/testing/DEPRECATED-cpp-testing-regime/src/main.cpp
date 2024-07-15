#include <Arduino.h>
#include <SPIMemory.h>
#include <DiagnosticsRun.h>
#include <CommandList.h>
#include <FlashHandler.h>
#include "main.h"

// The library we are using for this demo DOES NOT support QSPI
// Adafruit's SPI library may be able to help with this
// SPIMemory works for a wider range of cores, which is why it is used for this demo
// Adafruit SPI Flash only works for a nRF52, SAMD, RP2040 or ESP32
// Neither of these libraries work with an STM32, so are NOT to be used on any production ready cubesat
// This code is to ONLY be used for testing and validation purposes

#define BAUD_RATE 115200

String DUMMY_MSG = "Hello World!";

SPIFlash flash;

void setup()
{
  // begin flash
  Serial.begin(BAUD_RATE);

  // 50 ms delay to let chip bootup
  delay(50);
  flash.begin();
  Serial.println("Device ID:");
  Serial.println(flash.getJEDECID());
  Serial.println("Capacity:");
  Serial.println(flash.getCapacity());

  // display main command list
  mainlist();
  // let python script know arduino is ready
  Serial.println("<Arduino is ready>");
}

void loop()
{

  while (Serial.available() > 0)
  {

    uint8_t number = Serial.parseInt();
    switch (number)
    {
      // Run diagnostics
    case 0:
    {
      runDiagnostics(flash);
      break;
    }

    case 1:
    { // Write hello world and read it back
      readWriteString(flash, DUMMY_MSG);
      break;
    }
    case 2:
    {
      // dump data to the flash
      Serial.println("Dumping text to nand flash");
      Serial.println("This can take some time");
      readWriteString(flash, TEST_DATA);
      break;
    }
    case 3:
    {
      // this is our stress testing seg
      testlist();
      // wait for data to come through
      while (!Serial.available())
      {
      }
      uint8_t choice = Serial.parseInt();
      switch (choice)
      {
      case 1:
      {
        Serial.println("Dumping test data to nand flash");
        Serial.println("This can take some time");
        uint8_t addr = writeString(flash, TEST_DATA);
        Serial.println("Data written to: ");
        Serial.print(addr);
        break;
      }
      case 2:
      {
        Serial.println("Please enter the address the data was written to");
        // wait for data to come through
        while (!Serial.available())
        {
        }
        uint8_t addr = Serial.parseInt();
        Serial.println("Seeing if there is any data corruption: ");
        dataCompare(flash, addr, TEST_DATA);
      }

      default:
        Serial.println("Not a valid option!");
      }
      break;
    }
    default:
    {
      Serial.println("Not a valid command!");
      mainlist();
    }
    }
  }
}