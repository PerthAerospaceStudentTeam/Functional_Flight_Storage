#include <Arduino.h>
#include <SPIMemory.h>
#include <chrono>
#include "FlashHandler.h"

uint32_t writeString(SPIFlash flash, String &_string)
{
    unsigned long t1 = millis();
    uint32_t addr = flash.getAddress(flash.sizeofStr(_string));
    Serial.println("Writing to address: ");
    Serial.print(addr);
    if (flash.writeStr(addr, _string))
    {
        unsigned long t2 = millis();
        Serial.println("Wrote sucessfully!");
        Serial.println("Call time (in ms):");
        Serial.print(t2 - t1);
        return addr;
    }
    else
    {
        Serial.println("Data error");
        Serial.println(flash.error(true));
        return 0;
    }
}

// Read the string out to serial and return its length
uint16_t readStringToSerial(SPIFlash flash, uint32_t addr)
{
    unsigned long t1 = millis();

    String output_str;
    if (!flash.readStr(addr, output_str))
    {
        Serial.println("Data error");
        Serial.println(flash.error(true));
        return 0;
    }
    else
    {
        unsigned long t2 = millis();
        Serial.print(output_str);
        Serial.println("Call time (in ms):");
        Serial.print(t2 - t1);
        return flash.sizeofStr(output_str);
    }
}

void readWriteString(SPIFlash flash, String &_string)
{
    uint32_t addr = writeString(flash, _string);
    if (addr)
    {
        Serial.println("Reading back from address: ");
        Serial.println(addr);
        readStringToSerial(flash, addr);
    }
}

bool dataCompare(SPIFlash flash, uint32_t addr, String &compare_str)
{
    String output_str;
    if (!flash.readStr(addr, output_str))
    {
        Serial.println("Data error");
        Serial.println(flash.error(true));
        return false;
    }
    else
    {
        if (output_str == compare_str)
        {
            Serial.println("Data is the same. Cleaning up...");
            // Clear up dummy data
            flash.eraseSection(addr, flash.sizeofStr(compare_str));
            return true;
        }
        else
        {
            Serial.println("Data has corrupted. Attempting to erase...");
            Serial.println("Returned string:");
            Serial.println(output_str);
            flash.eraseSection(addr, flash.sizeofStr(output_str));
            return false;
        }
    }
}