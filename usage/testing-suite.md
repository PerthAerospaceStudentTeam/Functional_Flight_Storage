## SPI Memory

SPI testing will be done using the [`SPI Memory`](https://github.com/Marzogh/SPIMemory) package.
The tests that will be conducted is quite simple.

# Test Suite

#### Test Zero - Connection Evaluation

This test is quite simple - using a multimeter, we will evaluate all physical connections are connected

#### Test One - Basic Test

We will write 12 bytes to the storage chip. This will be done with the string `Hello World!`. The goal if this test is to validate that we can write data to the chip.

Once the data is written, it will be read back. The test is successful when the complete string is read back

We can use the example code on the SPI Memory page [here](https://github.com/Marzogh/SPIMemory/blob/master/examples/readWriteString/readWriteString.ino)

#### Test Two - Running Test

We will write 100 Kilobytes of data. This is to test overall performance of the chip. The sample data can be found in `data.txt`

The following equipment will be used

- Multimeter to measure the amperage and voltage
- Oscilloscope to ensure signals are good

The test will be functionally identical to Test One. Timing code will be injected to measure how long the write transfer, and then the subsequent read transfer will take

#### Test Three - Overflow Test

The aim of this test is to evaluate whether we can 'break' the board through testing its limits. To do this, we will try and write the full copy of Kerbal Space Program to the storage chip. This takes up 400Mb of data - greatly exceeding the storage capacity of any chip. In theory, the chip should reject this. Let's see what happens

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
| MT29F2G08ABAEAWP-AATX:E TR | Y†     |        |        |        |        |
| AT25EU0081A-SSUN-T         | Y      | Y††    |        |        |        |
† Bridging between contacts of the chip observed, however the contacts are no connects
†† Tested using a D1 mini
