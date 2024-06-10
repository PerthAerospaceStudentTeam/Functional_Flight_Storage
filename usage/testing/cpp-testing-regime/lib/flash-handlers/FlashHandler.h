#include <Arduino.h>
#include <SPIMemory.h>

uint32_t writeString(SPIFlash flash, String &_string);
uint16_t readStringToSerial(SPIFlash flash, uint32_t addr);
void readWriteString(SPIFlash flash, String &_string);
bool dataCompare(SPIFlash flash, uint32_t addr, String &compare_str);