#include <Arduino.h>
#include <SPIMemory.h>

// Function prototypes
void printLine();
void printTab(uint8_t _times);
void printTime(uint32_t _wTime, uint32_t _rTime);
void printTimer(uint32_t _us);
void pass(bool _status);
void printUniqueID(SPIFlash flash);
bool getID(SPIFlash flash);
void byteTest(SPIFlash flash);
void charTest(SPIFlash flash);
void wordTest(SPIFlash flash);
void shortTest(SPIFlash flash);
void uLongTest(SPIFlash flash);
void longTest(SPIFlash flash);
void floatTest(SPIFlash flash);
void stringTest(SPIFlash flash);
void structTest(SPIFlash flash);
void arrayTest(SPIFlash flash);
void powerDownTest(SPIFlash flash);
void powerUpTest(SPIFlash flash);
void eraseSectorTest(SPIFlash flash);
void eraseSectionTest(SPIFlash flash);
void eraseBlock32KTest(SPIFlash flash);
void eraseBlock64KTest(SPIFlash flash);
void eraseChipTest(SPIFlash flash);
