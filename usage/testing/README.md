## cpp-testing-regime

All chips that use SPI will be done using the [`SPI Memory`](https://github.com/Marzogh/SPIMemory) package. This package does have a built in diagnostics routine, to test performance of all commands. This can be run through the testing regime program
For ease of use, a complete testing regime has been written in order to make testing a lot easier. It can be found in `cpp-testing-regime`. 
Note that it has been built with [PlatformIO](https://platformio.org/), and should be opened with it in order to make best use of the tooling
The code has been written for an Arduino-based D1 Mini, as that is the only 3v3 logic board I had lying around to test with. Using a differnt board should be as simple as changing the board defined in `platform.ini`, provided it is supported by the [SPIMemory](https://github.com/Marzogh/SPIMemory) library

## ONFIDriver

The MT29F2G08ABAEAWP chip does not have any off the self drivers that we can use. Because of this, a custom driver has been written in Python in order to evaluate the performance of the chip. Whilst Python is not the fastest language, it will suffice to test a) whether this chip works and b) how well it works

# Test Suite

#### Test Zero - Connection Evaluation

This test is quite simple - using a multimeter, we will evaluate all physical connections are connected

#### Test One - Read ID

We will attempt to read the ID from the storage chip. This is to validate that the chip is functional

#### Test Two - Basic Test

We will write 12 bytes to the storage chip. This will be done with the string `Hello World!`. The goal if this test is to validate that we can write data to the chip.

Once the data is written, it will be read back. The test is successful when the complete string is read back

We can use the example code on the SPI Memory page [here](https://github.com/Marzogh/SPIMemory/blob/master/examples/readWriteString/readWriteString.ino)

#### Test Three - Running Test

We will write 40 Kilobytes of data. This is to test overall performance of the chip. The sample data can be found in `data.txt`

The following equipment will be used

- Multimeter to measure the amperage and voltage
- Oscilloscope to ensure signals are good

The test will be functionally identical to Test One. Timing code will be injected to measure how long the write transfer, and then the subsequent read transfer will take

#### Test Four - Stress Test

Continuing from Test Two, this test will explore how well the chip can store data with no power and in extreme states

The test begins by writing the `data.txt` to the the chip. The chip will then be placed in two environments (with its power off)

The chip will then be placed in three environments

1. 60 degrees celsius for 30 minutes
2. -10 degrees celsius for 30 minutes
3. 5mA input current.

Data should be able to read after test 1. and 2. have occurred. Test 3 will be run with the current increasing until data is able to be read

# Test Results
| Chip                       | Test 0 | Test 1 | Test 2 | Test 3 | Test 4 |
|----------------------------|--------|--------|--------|--------|--------|
| W25N01GVSFIG               | Y      |        |        |        |        |
| MT29F2G08ABAEAWP-AATX:E TR | Y†     | Y†††   | Y†††   | Y†††   |        |
| AT25EU0081A-SSUN-T         | Y      | Y††    | Y††    |        |        |

† Bridging between contacts of the chip observed, however the contacts are no connects

†† Tested using a D1 mini
††† Tested using a Raspberry Pi Pico


#### MT29F2G08ABAEAWP-AATX:E TR

##### Reading
With the raspberry pi pico using PIO, reading 16800 bytes took 84 seconds, this gives a speed of 200 bytes per second
With a second test, with the raspberry pi pico using PIO, reading 84480 bytes took 404.91 seconds, giving a speed of ~208 bytes per second
With a third test, with the raspberry pi pico using PIO, reading 84480 bytes took 396.167 seconds, giving a speed of ~213 bytes per second
Without PIO, reading 16800 bytes took ~110 seconds, giving a speed of 153 bytes per second

##### Writing
Writing 40kb took 118.622 seconds, giving a time of ~333 bytes per second
With a second test, utilising all bytes in a page, writing 30kb took 76.513 seconds, giving a time of ~522 bytes per second (using the programPageString function, as it may utilise less memory)

This can definitely be improved by using an STM32, or using PIO for read and write on the raspberry pi pico as the chip's max speed is about 84,480,000 bytes per second for read, and 10,560,000 bytes per second for write

For Test 3, the chip has not been tested with a:
- Multimeter to measure the amperage and voltage
- Oscilloscope to ensure signals are good

##### Usage of Raspberry Pi Pico driver & Testing
There are three drivers, any one of them should be able to run, however they have their differences
- ONFIDriver.py is the default driver, it should run normal with no errors
- ONFIDriver_2.py is nearly identical to the default driver, however it has removed the fanatics of the wait times, assuming that the program is running slow enough where the wait times will be reached, however in practice, there is no observed large difference with the default driver in terms of speed (more testing required)
- ONFIDriverParallel.py is similar to the default driver, however PIO is used to read pins, which increases speed dramatically, leading to about 30% increase in speed for reading, PIO is NOT used to write to the pins, due to problems (TODO: Fix PIO write), however due to write not requiring a change of Pin state, it is already quick enough for programming the NAND chip, it would however still improve the overall speed. There is a few observed problems with using the PIO driver, due to using assembly, I do not fully understand how PIO works, and so it may sometimes have previous bytes in the registers and may include those in the next function. When calling status, it may also bit shift the values, causing a problem

The drivers all have the same functions, currently:
- Helper functions:
    - toByte(value) will convert a value to an 8 bit value of type string e.g. "00000000"
    - stringToByte(string) will convert a string to binary, having a length of a multiple of 8
    - verifyColumnAddress(columnAddress) and verifyAddress(columnAddress, pageAddress, blockAddress) are used to make sure the addresses to the chip are valid, returning false if not valid
- Raw operations
    - setPins() (ONFIDriverParallel.py only) will set the state of Pins to all be inputs, SHOULD be called before a readPins() command, preferable as early as possible after a writeCommand() or writeAddress()
    - readRaw() will read the values of the pins without toggling read enable, sometimes used to clean out the registers
    - readPins() will read the values of the pins, toggling read enable - Will actually get useful data
    - writePins(data) will write the 8 bit data to the pins, toggling write enable - This sends data to the NAND chip
    - writeCommand(data) will call writePins(data) but toggles command latch enable - This sends a command to the NAND chip
    - writeAddress(data) will call writePins(data) but toggles the address latch enable - This sends an address to the NAND chip
- Functions:
    - reset() will reset the chip, MUST be called before powerup
    - readID() will read the chip ID and ONFI ID of the chip, should print "ONFI" for the ONFI ID
    - readParameterPage(length) will return the data from the parameter page, a length is specified as the chip can theoretically return 999+ lines
    - setFeatures(featureAddress, value) will set the value to the feature, this is used to enable or disable ECC, WARMING: reserved bits are not verified in this command
    - getFeatrues(featureAddress) will return the value of the feature
    - status() will return 8 bits corresponding to the status of the chip
- Column address operations (Not really sure when to use these, however they are implemented)
    - columnRandReadC(columnAddress, length) will read data from the columnAddress at the current page and block, potentially used to quickly switch columns when reading multiple times
    - columnRandReadP(columnAddress, pageAddress, blockAddress, length) will read data from the specified addresses, not sure what the advantage is
    - columnRandInput(columnAddress, data) is supposed to write data to a columnAddress, NOT TESTED TO WORK
- Read operations
    - readMode() will set the chip to readMode(), sometimes required after going into status mode
    - readPage(columnAddress, pageAddress, blockAddress, length, ecc=False), will read data of length from a specified address, set ecc to True if ecc is turned on
    - readPageCacheSequential(columnAddress, pageAddress, blockAddress, length, pages, ecc=False, end=True) used to sequentially read data, it should be used to improve read speeds, by default, it will assume to only read the specified number of pages, but when end=False, can be used with readPageCacheSequentialContinued() to read larger data sequentially without running out of memory
    - readPageCacheSequentialContinued(length, pages, ecc=False, end=False) is used to continue to read sequential data
    - readPageCacheLast(length) will end the readSequential function, and also return data of the last specified page
- Program operations
    - programPage(columnAddress, pageAddress, blockAddress, data) will program a page at the address with the data in binary
    - programPageString(columnAddress, pageAddress, blockAddress, data) will achieve the same as programPage(), however it will accept a string, converting it to a binary value before writing it, this can be quicker than using programPage()
- Erase operations
    - eraseBlock(pageAddress, blockAddress) will erase the block specified by the blockAddress, pageAddress will be ignored by the NAND chip
- initialise() will enable the chip, resetting it, and set all control values to default ones

initialise() should be called at the start only

A typical read would use readPage(), if large amounts of data is utilised, readPageSequentional should used
A typical write would use either programPage() or programPageString() depending on data type, make sure to eraseBlock() before writing data over an area with already written data

Use FlashStorage.py for demonstration of the main features