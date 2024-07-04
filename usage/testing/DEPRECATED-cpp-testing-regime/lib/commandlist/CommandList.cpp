#include <Arduino.h>
#include "CommandList.h"

// Inspired by https://github.com/Marzogh/SPIMemory/blob/master/examples/TestFlash/command_list.ino

void mainlist()
{
    Serial.println(F("-----------------------------------------------------------------------------------------------------------------------------------"));
    Serial.println(F("                                                        FFS Testing Suite v1.0.0                                                   "));
    Serial.println(F(" ----------------------------------------------------------------------------------------------------------------------------------"));
    Serial.println(F("                                                      Developed by Sean McDougall                                                  "));
    Serial.println(F("                                                              08.06.2024                                                           "));
    Serial.println(F(" ----------------------------------------------------------------------------------------------------------------------------------"));
    Serial.println(F("                                      (Please make sure your Serial monitor is set to 'No Line Ending')                            "));
    Serial.println(F("                                      *****************************************************************                            "));
    Serial.println(F("                                                                                                                                   "));
    Serial.println(F("                      # Please pick from the following commands and type the command number into the Serial console #              "));
    Serial.println(F("                                         For example - to run Test '1', type 1 into the console                                    "));
    Serial.println(F("                                                     --------------------------------                                              "));
    Serial.println();
    Serial.println(F("  0. Run Diagnostics"));
    Serial.print(F("\t\t"));
    Serial.println(F("'0' runs the SPIMemory diagnostics suite"));
    Serial.println(F("  1. Read/Write Test"));
    Serial.print(F("\t\t"));
    Serial.println(F("'1' write 'Hello World!' to a random address in the flash chip and read it back"));
    Serial.println(F("  2. dump data"));
    Serial.print(F("\t\t"));
    Serial.println(F("'2' dumps 100kB of data into the flash chip and reads it back"));
    Serial.println(F("  3. stress test"));
    Serial.print(F("\t\t"));
    Serial.println(F("'3' set up/tear down the flash chip for stress testing"));
    Serial.println(F(" ----------------------------------------------------------------------------------------------------------------------------------"));
}

void testlist()
{
    Serial.println(F("-----------------------------------------------------------------------------------------------------------------------------------"));
    Serial.println(F("                                                    FFS Stress Testing Suite v1.0.0                                                "));
    Serial.println(F(" ----------------------------------------------------------------------------------------------------------------------------------"));
    Serial.println(F("                                                      Developed by Sean McDougall                                                  "));
    Serial.println(F("                                                              08.06.2024                                                           "));
    Serial.println(F(" ----------------------------------------------------------------------------------------------------------------------------------"));
    Serial.println(F("                                      (Please make sure your Serial monitor is set to 'No Line Ending')                            "));
    Serial.println(F("                                      *****************************************************************                            "));
    Serial.println(F("                                                                                                                                   "));
    Serial.println(F("                                          3 stress tests must be run on each prospective chip:                                     "));
    Serial.println(F("                                                                                                                                   "));
    Serial.println(F("                                      1. Heat the chip up to 60 degrees celsius for 30 minutes                                     "));
    Serial.println(F("                                      2. Cool the chip down to -10 degrees celsius for 30 minutes                                  "));
    Serial.println(F("                                      3. Run the chip at 5mA, and increase current until data can be read                          "));
    Serial.println(F("                                                     --------------------------------                                              "));
    Serial.println();
    Serial.println(F("  1.  Write data"));
    Serial.print(F("\t\t"));
    Serial.println(F("'1' write data to the chip before the test"));
    Serial.println(F("  2. Read data"));
    Serial.print(F("\t\t"));
    Serial.println(F("'2' read and clear the data after the test"));
}