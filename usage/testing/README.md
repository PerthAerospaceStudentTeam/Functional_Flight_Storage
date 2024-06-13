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
| MT29F2G08ABAEAWP-AATX:E TR | Y†     | Y†††   | Y†††   |        |        |
| AT25EU0081A-SSUN-T         | Y      | Y††    | Y††    |        |        |

† Bridging between contacts of the chip observed, however the contacts are no connects

†† Tested using a D1 mini
††† Tested using a Raspberry Pi Pico