## cpp-testing-regime

All chips that use SPI will be done using the [`SPI Memory`](https://github.com/Marzogh/SPIMemory) package. This package does have a built in diagnostics routine, to test performance of all commands. This can be run through the testing regime program
For ease of use, a complete testing regime has been written in order to make testing a lot easier. It can be found in `cpp-testing-regime`. 
Note that it has been built with [PlatformIO](https://platformio.org/), and should be opened with it in order to make best use of the tooling
The code has been written for an Arduino-based D1 Mini, as that is the only 3v3 logic board I had lying around to test with. Using a differnt board should be as simple as changing the board defined in `platform.ini`, provided it is supported by the [SPIMemory](https://github.com/Marzogh/SPIMemory) library

## ONFIDriver

The MT29F2G08ABAEAWP chip does not have any off the self drivers that we can use. Because of this, a custom driver has been written in Python in order to evaluate the performance of the chip. Whilst Python is not the fastest language, it will suffice to test a) whether this chip works and b) how well it works

## FMC NAND Driver

It was found that on the STM32, the FMC NAND Driver can be used for the MT29F2G08ABAEAWP chip

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

Continuing from Test Three, this test will explore how well the chip can store data with no power and in extreme states

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
| MT29F2G08ABAEAWP-AATX:E TR | Y†     | Y††††  | Y††††  | Y††††  |        |
| AT25EU0081A-SSUN-T         | Y      | Y††    | Y††    |        |        |

† Bridging between contacts of the chip observed, however the contacts are no connects

†† Tested using a D1 mini

††† Tested using a Raspberry Pi Pico

†††† Tested using a Raspberry Pi Pico and STM32 (Using FMC)

#### MT29F2G08ABAEAWP-AATX:E TR
### FMC NAND Driver
##### Config
Setting all times to 64 HCLK should be safe, as running at 64 MHZ, 1 HCLK would be ~16ns, and 64 HCLK would be ~1us, which should be plenty of time

Setup time - highest min is 10ns min (ALE), with exception of 15ns min (CE#)
Hold time - 5ns min

Wait time - (WE high to RE low 60ns min), (ALE to data start 70ns min), (WP# to WE# low 100ns min)

High Z - (RE# high to output high-Z 100ns max)

Erase operation time 0.7-3ms
Program page 200-600us (room temp) - Should read status after, as there is no wait within the driver

Therefore to be safe we will give setup time 2 HCLK, wait time 8 HCLK, hold time 2 HCLK, Hi-Z 8 HCLK (2-8-2-8)

If we wanted to push the chip, we could try 1-7-1-7

##### Code snippet
```cpp
HAL_NAND_Reset(&hnand1);
NAND_IDTypeDef id;
HAL_NAND_Read_ID(&hnand1, &id);

HAL_NAND_ECC_Enable(&hnand1);
HAL_NAND_Read_Status(&hnand1);
uint8_t data[64*2112*2];

NAND_AddressTypeDef pAddress;
pAddress.Plane = 0;
pAddress.Block = 1;
pAddress.Page = 0;
uint32_t tick = HAL_GetTick();
HAL_NAND_Read_Page_8b(&hnand1, &pAddress, &data, 128);
tick = HAL_GetTick() - tick;

pAddress.Plane = 0;
pAddress.Block = 2;
pAddress.Page = 0;
//uint32_t tick2 = HAL_GetTick();
//HAL_NAND_Erase_Block(&hnand1, &pAddress);
//tick2 = HAL_GetTick() - tick2;

uint32_t tick3 = HAL_GetTick();
HAL_NAND_Write_Page_8b(&hnand1, &pAddress, &data, 128);
tick3 = HAL_GetTick() - tick3;
```

##### Reading (ECC Enabled)
With the STM32 at default (unchanged max wait times) settings, reading 135168 bytes took 1.737 seconds, giving a speed of ~77817 bytes per second (~76 kbytes per second)
With some tweaking of time settings (setting times to 64 HCLK), reading 135168 bytes took 0.517 seconds, giving a speed of ~255kb/s

Tweaking the time settings to 2-8-2-8, reading 135168 bytes took 0.137 seconds, giving a speed of ~963.5kb/s (~0.941mb/s)

Tweaking the time settings to 1-7-1-7, reading 135168 bytes took 0.131 seconds, giving a speed of ~0.984mb/s

Tweaking the time settings to 1-1-1-1, reading 135168 bytes took 0.120 seconds, giving a speed of ~1.074mb/s

With 2-8-2-8, reading 270336 bytes took 0.275 seconds, giving a speed of ~0.9375mb/s

##### Writing (ECC Enabled)
At 64 HCLK, writing 135168 bytes took 0.418 seconds, giving a speed of ~315kb/s

Tweaking the time settings to 2-8-2-8, writing 135168 bytes took 0.146 seconds, giving a speed of ~904kb/s (~0.883mb/s)

Tweaking the time settings to 1-7-1-7, writing 135168 bytes took 0.145 seconds, giving a speed of ~0.889mb/s

Tweaking the time settings to 1-2-1-1, writing 135168 bytes took 0.145 seconds, giving a speed of ~0.889mb/s


With 2-8-2-8, writing 270336 bytes took 0.291 seconds, giving a speed of ~0.886mb/s

#### Python ONFI Driver
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

Refer to [here](https://github.com/RaphGamingz/BasicONFIDriver/tree/main) for the driver functionality
