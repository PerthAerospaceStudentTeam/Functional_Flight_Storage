## cpp-testing-regime - WAS NOT USED

All chips that use SPI will be done using the [`SPI Memory`](https://github.com/Marzogh/SPIMemory) package. This package does have a built in diagnostics routine, to test performance of all commands. This can be run through the testing regime program
For ease of use, a complete testing regime has been written in order to make testing a lot easier. It can be found in `cpp-testing-regime`. 
Note that it has been built with [PlatformIO](https://platformio.org/), and should be opened with it in order to make best use of the tooling
The code has been written for an Arduino-based D1 Mini, as that is the only 3v3 logic board I had lying around to test with. Using a differnt board should be as simple as changing the board defined in `platform.ini`, provided it is supported by the [SPIMemory](https://github.com/Marzogh/SPIMemory) library

After some tests, it was found that the W25N01GVSFIG did not work very well with the [`SPI Memory`](https://github.com/Marzogh/SPIMemory) package, and so custom drivers and testing routines were developed

## ONFIDriver

The MT29F2G08ABAEAWP chip does not have any off the self drivers that we can use. Because of this, a custom driver has been written in Python in order to evaluate the performance of the chip. Whilst Python is not the fastest language, it will suffice to test a) whether this chip works and b) how well it works

## FMC NAND Driver

It was found that on the STM32, the FMC NAND Driver can be used for the MT29F2G08ABAEAWP chip

## Custom Driver for the W25N01GVSFIG
Whilst the [`SPI Memory`](https://github.com/Marzogh/SPIMemory) did have good support for the chips, it did not support many of the commands for the W25N01GVSFIG. A custom driver was written in Rust (mainly because I wasn't really thinking and wanted to try something new)

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

The test begins by writing the `data.txt` to the the chip
A thermal camera will be used to measure the temperature of the chip while running
Current will be measured to find the power draw of the chip

# Test Results
| Chip                       | Test 0 | Test 1 | Test 2 | Test 3 | Test 4 |
|----------------------------|--------|--------|--------|--------|--------|
| W25N01GVSFIG               | Y      | Y      | Y      | Y      | Y†††   |
| MT29F2G08ABAEAWP-AATX:E TR | Y†     | Y      | Y      | Y      | Y†††   |
| AT25EU0081A-SSUN-T         | Y      | Y††    | Y††    |        |        |

† Bridging between contacts of the chip observed, however the contacts are no connects

†† Tested using a D1 mini

††† Temperature difference was negligible & power draw could not be measured


## Summary
| Chip                       | Read Speed                          | Write Speed      | Number of Pins |
|----------------------------|-------------------------------------|------------------|----------------|
| W25N01GVSFIG               | @240MHz, 158kb/s                    | @240MHz, 50kb/s  | 4+2=6          |
| MT29F2G08ABAEAWP-AATX:E TR | @200MHz 2.86mb/s typ, 4.02mb/s max  | @200MHz 2.86mb/s | 8+7=15         |
| AT25EU0081A-SSUN-T         | 133kb/s                             | 8.5kb/s          | 4+2=6          |

## W25N01GVSFIG
Peak speeds were averaged over three times with the data from Test 3. 
- Peak write took 0.803635 seconds for 40Kb of data (50kb/s). 
- Peak read took 0.251840 for 40Kb of data (158kb/s).

#### Functions supported by the Driver
- Writing a byte and a data structure
- Reading back a byte or a page
- Reading back a data structure of known (slow) or unknown length (slower)

#### Improvements to the Driver
The driver is certainly not the fastest. There a quite a few improvements that could be made to the code. In no particular order
- The driver started out using the QSPI interface. However, the HAL I am using does not support changing between SPI and QSPI between different transaction phases. This means the instruction was being sent across 4 channels, whereas the chip expected it on the MOSI channel only. This was discovered too late in the development, and so QSPI is still being used, but in the SingleLine mode
- The QSPI interface only supports 32 byte transfers at a time, meaning it has to be buffered out which is very slowly
- The HAL also waits between 50-100microseconds between each transaction, which adds up considerably (especially if only 32 bytes is sent at a time)
In theory, QSPI would speed up the chip by 4 times, and various optimisations to the code could result in an additional 1.5 times speed boost.

The Driver also doesn't make full use of the ECC onboard the chip. Whilst we do let the ECC bits get written, and so the chip handles that side of data integrity, we do not poll the status register to see if there is an irrecoverable ECC corruption

With a better driver, the theoretical performance would be
- Write Speed: 250kb/s
- Read Speed: 790 kb/s

## MT29F2G08ABAEAWP-AATX:E TR
Fastest & safest speed reached was 2.86mb/s read and write
Fastest read speed reached was 4.02mb/s, however we are unsure if the data was all read correctly

### FMC NAND Driver
#### Config
Setting all times to 64 HCLK should be safe, as running at 64 MHz, 1 HCLK would be ~16ns, and 64 HCLK would be ~1us, which should be plenty of time

Setup time - highest min is 10ns min (ALE), with exception of 15ns min (CE#)
Hold time - 5ns min

Wait time - (WE high to RE low 60ns min), (ALE to data start 70ns min), (WP# to WE# low 100ns min)

High Z - (RE# high to output high-Z 100ns max)

Erase operation time 0.7-3ms
Program page 200-600us (room temp) - Should read status after, as there is no wait within the driver

ALE to RE# & CLE to RE# delay 10ns min

#### Timings @ 200 MHz
ALE to RE delay & CLE to RE delay would be set to 2 HCLK

200 MHz is not the fastest FMC can run (it can run up to 240 MHz), however it would require non-whole clock cycles to run (probably taking up more time)
Using 200 MHz means that one HCLK is 5ns
The timings would be 3-20-2-20
If we were to push it, it we could try 2-20-1-20

To really push it, 2-10-1-10 was also tested, however data integrity could be a problem (unverified)
- Benefits to this was a faster read speed, but approx same write speed

##### Reading @200 MHz
3-20-2-20: Reading 135168 bytes took 0.047 seconds, giving a speed of ~2.74mb/s

2-20-1-20: Reading 135168 bytes took 0.045 seconds, giving a speed of ~2.86mb/s

2-10-1-10: Reading 135168 bytes took 0.032 seconds, giving a speed of ~4.02mb/s

##### Writing @200 MHz
3-20-2-20: Writing 135168 bytes took 0.045 seconds, giving a speed of ~2.86mb/s

2-20-1-20: Writing 135168 bytes took 0.045 seconds, giving a speed of ~2.86mb/s

2-10-1-10: Writing 135168 bytes took 0.046 seconds, giving a speed of ~2.80mb/s (SLOWER)

#### Timings @ 64 MHz
ALE to RE delay & CLE to RE delay would be set to 1 HCLK

64 MHz is the default speed
The timings would be 2-8-2-8
If we wanted to push the chip, we could try 1-7-1-7

To really push it, 1-1-1-1 was also tested, however data integrity could be a problem (unverified)
##### Reading @64 MHz
With the STM32 at default (unchanged max wait times) settings, reading 135168 bytes took 1.737 seconds, giving a speed of ~77817 bytes per second (~76 kbytes per second)
64-64-64-64: Reading 135168 bytes took 0.517 seconds, giving a speed of ~255kb/s

2-8-2-8: Reading 135168 bytes took 0.137 seconds, giving a speed of ~0.941mb/s

1-7-1-7: Reading 135168 bytes took 0.131 seconds, giving a speed of ~0.984mb/s

1-1-1-1: Reading 135168 bytes took 0.120 seconds, giving a speed of ~1.074mb/s


2-8-2-8: Reading 270336 bytes took 0.275 seconds, giving a speed of ~0.9375mb/s

##### Writing @64 MHz
64-64-64-64: Writing 135168 bytes took 0.418 seconds, giving a speed of ~315kb/s

2-8-2-8: Writing 135168 bytes took 0.146 seconds, giving a speed of ~0.883mb/s

1-7-1-7: Writing 135168 bytes took 0.145 seconds, giving a speed of ~0.889mb/s

1-2-1-1: Writing 135168 bytes took 0.145 seconds, giving a speed of ~0.889mb/s


2-8-2-8: Writing 270336 bytes took 0.291 seconds, giving a speed of ~0.886mb/s

#### Further improvements
The driver does not seem to use the ECC builtin on the chip, this could be enabled
The driver does not use cache sequential read, however it is not supported with ECC, although if software ECC is used, it would possibly be able to improve speeds slightly

### Python ONFI Driver
#### Reading
With the raspberry pi pico using PIO, reading 16800 bytes took 84 seconds, this gives a speed of 200 bytes per second
With a second test, with the raspberry pi pico using PIO, reading 84480 bytes took 404.91 seconds, giving a speed of ~208 bytes per second
With a third test, with the raspberry pi pico using PIO, reading 84480 bytes took 396.167 seconds, giving a speed of ~213 bytes per second
Without PIO, reading 16800 bytes took ~110 seconds, giving a speed of 153 bytes per second

#### Writing
Writing 40kb took 118.622 seconds, giving a time of ~333 bytes per second
With a second test, utilising all bytes in a page, writing 30kb took 76.513 seconds, giving a time of ~522 bytes per second (using the programPageString function, as it may utilise less memory)

This can definitely be improved by using an STM32, or using PIO for read and write on the raspberry pi pico as the chip's max speed is about 84,480,000 bytes per second for read, and 10,560,000 bytes per second for write

For Test 3, the chip has not been tested with a:
- Multimeter to measure the amperage and voltage
- Oscilloscope to ensure signals are good
