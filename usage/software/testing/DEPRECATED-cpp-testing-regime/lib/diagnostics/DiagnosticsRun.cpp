#include <Arduino.h>
#include <SPIMemory.h>
#include <Diagnostics.h>
#include "Diagnostics.h"

// Taken from SPIMemory example code: https://github.com/Marzogh/SPIMemory/tree/master/examples/FlashDiagnostics

void runDiagnostics(SPIFlash flash)
{
    if (flash.error())
    {
        Serial.println(flash.error(VERBOSE));
    }
    else
    {
        if (getID(flash))
        {
            printLine();
            printTab(7);
            Serial.print("Testing library code");
            printLine();
            printTab(3);
            Serial.print("Function");
            printTab(2);
            Serial.print("Test result");
            printTab(3);
            Serial.print("     Runtime");
            printLine();
            powerDownTest(flash);
            Serial.println();
            powerUpTest(flash);
            Serial.println();
            Serial.println();
            eraseChipTest(flash);
            Serial.println();
            eraseSectionTest(flash);
            Serial.println();
            eraseBlock64KTest(flash);
            Serial.println();
            eraseBlock32KTest(flash);
            Serial.println();
            eraseSectorTest(flash);
            printLine();
            printTab(3);
            Serial.print("Data type");
            printTab(2);
            Serial.print("I/O Result");
            printTab(1);
            Serial.print("      Write time");
            printTab(1);
            Serial.print("      Read time");
            printLine();
            byteTest(flash);
            Serial.println();
            charTest(flash);
            Serial.println();
            wordTest(flash);
            Serial.println();
            shortTest(flash);
            Serial.println();
            uLongTest(flash);
            Serial.println();
            longTest(flash);
            Serial.println();
            floatTest(flash);
            Serial.println();
            structTest(flash);
            Serial.println();
            arrayTest(flash);
            Serial.println();
            stringTest(flash);
            printLine();
            if (!flash.functionRunTime())
            {
                Serial.println(F("To see function runtimes ncomment RUNDIAGNOSTIC in SPIMemory.h."));
            }
        }
    }
}