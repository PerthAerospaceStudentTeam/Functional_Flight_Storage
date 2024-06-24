# Hardware

To use the chip in a hardware setting, simply take the Altium files found in [`/pcb/altium`](https://github.com/PerthAerospaceStudentTeam/past-storage/blob/main/pcb/altium/README.md), and place them in the desired project.

The pinouts are as follows

| Pin  | Connect | Use                                                                                                |
| ---- | ------- | -------------------------------------------------------------------------------------------------- |
| +3v3 | +3v3    | Provide power to the board                                                                         |
| GND  | GND     | Provide ground to the board                                                                        |
| CLK  | CLK     | Provides the clock signal - can be connected to external clock provided it is shared between chips |
| IO0  | QSPI0   | Data I/O - see image for STM32 ref.                                                                |
| IO1  | QSPI1   | Data I/O - see image for STM32 ref.                                                                |
| IO2  | QSPI2   | Data I/O - see image for STM32 ref.                                                                |
| IO3  | QSPI3   | Data I/O - see image for STM32 ref.                                                                |

For an STM32 Nucleo (the development used), the following QSPI pinout can be used

![pinout](https://os.mbed.com/media/uploads/jeromecoutant/nucleo_h743zi_zio_right_2019_8_29.png)

For a dedicated MCU, connect the corresponding QSPI lines to the memory

The pinouts for the parallel interface are as follows for the raspberry pi pico
| Pin  | Connect | Use                                                                                                |
| ---- | ------- | -------------------------------------------------------------------------------------------------- |
| +3v3 | 3V3(Out)| Provide power to the board                                                                         |
| GND  | GND     | Provide ground to the board                                                                        |
| WP#  | GP19   | Write Protect active low - Pulled low |
| WE#  | GP18   | Write Enable active low |
| AL   | GP15   | Address Latch Enable - Load address from IO into address register |
| CL   | GP14   | Command Latch Enable - Load address from IO into command register |
| CE#  | GP17   | Chip enable active low - Pulled high |
| RE#  | GP16   | Read enable active low - Pulled high |
| RB#  | N/C    | Ready/Busy active low - Pulled up |
| IO0  | GP6    | Data I/O                                                                |
| IO1  | GP7    | Data I/O                                                                |
| IO2  | GP8    | Data I/O                                                                |
| IO3  | GP9    | Data I/O                                                                |
| IO4  | GP10   | Data I/O                                                                |
| IO5  | GP11   | Data I/O                                                                |
| IO6  | GP12   | Data I/O                                                                |
| IO7  | GP13   | Data I/O                                                                |


The pinouts for the parallel interface are as follows for the stm32
| Pin  | Connect | Use                                                                                                |
| ---- | ------- | -------------------------------------------------------------------------------------------------- |
| +3v3 | 3v3     | Provide power to the board                                                                         |
| GND  | GND     | Provide ground to the board                                                                        |
| WP#  | PD_7   | Write Protect active low - Pulled low |
| WE#  | PD_5   | Write Enable active low |
| AL   | PD_12  | Address Latch Enable - Load address from IO into address register |
| CL   | PD_11  | Command Latch Enable - Load address from IO into command register |
| CE#  | PC_8  | Chip enable active low - Pulled high |
| RE#  | PD_4   | Read enable active low - Pulled high |
| RB#  | PD_6   | Ready/Busy active low - Pulled up |
| IO0  | PD_14  | Data I/O                                                                |
| IO1  | PD_15  | Data I/O                                                                |
| IO2  | PD_0   | Data I/O                                                                |
| IO3  | PD_1   | Data I/O                                                                |
| IO4  | PE_7   | Data I/O                                                                |
| IO5  | PE_8   | Data I/O                                                                |
| IO6  | PE_9   | Data I/O                                                                |
| IO7  | PE_10  | Data I/O                                                                |

# Software
### MT29 STM32 FMC example code:
```cpp
HAL_NAND_Reset(&hnand1);
NAND_IDTypeDef id;
HAL_NAND_Read_ID(&hnand1, &id);

//HAL_NAND_ECC_Enable(&hnand1);
HAL_NAND_Read_Status(&hnand1);
uint8_t hello[2112];
uint8_t h[12] = {'H', 'e', 'l', 'l', 'o', ' ', 'W', 'o', 'r', 'l', 'd', '!'};

NAND_AddressTypeDef pAddress;
pAddress.Plane = 0;
pAddress.Block = 0;
pAddress.Page = 0;
// Test 2
HAL_NAND_Read_Page_8b(&hnand1, &pAddress, &hello, 1);

HAL_NAND_Write_Page_8b(&hnand1, &pAddress, &h, 1);

HAL_NAND_Read_Page_8b(&hnand1, &pAddress, &hello, 1);

pAddress.Plane = 0;
pAddress.Block = 1;
pAddress.Page = 0;
uint8_t data[64*2112];

// Test 3
uint32_t tick = HAL_GetTick();
HAL_NAND_Read_Page_8b(&hnand1, &pAddress, &data, 64);
tick = HAL_GetTick() - tick;

pAddress.Plane = 0;
pAddress.Block = 2;
pAddress.Page = 0;
//uint32_t tick2 = HAL_GetTick();
//HAL_NAND_Erase_Block(&hnand1, &pAddress);
//tick2 = HAL_GetTick() - tick2;

uint32_t tick3 = HAL_GetTick();
HAL_NAND_Write_Page_8b(&hnand1, &pAddress, &data, 64);
tick3 = HAL_GetTick() - tick3;
```
### Python ONFI Driver
There are three drivers, any one of them should be able to run, however they have their differences
- ONFIDriver.py is the default driver, it should run normal with no errors
- ONFIDriver_2.py is nearly identical to the default driver, however it has removed the fanatics of the wait times, assuming that the program is running slow enough where the wait times will be reached, however in practice, there is no observed large difference with the default driver in terms of speed (more testing required)
- ONFIDriverParallel.py is similar to the default driver, however PIO is used to read pins, which increases speed dramatically, leading to about 30% increase in speed for reading, PIO is NOT used to write to the pins, due to problems (TODO: Fix PIO write), however due to write not requiring a change of Pin state, it is already quick enough for programming the NAND chip, it would however still improve the overall speed. There is a few observed problems with using the PIO driver, due to using assembly, I do not fully understand how PIO works, and so it may sometimes have previous bytes in the registers and may include those in the next function. When calling status, it may also bit shift the values, causing a problem

Refer to [here](https://github.com/RaphGamingz/BasicONFIDriver/tree/main) for the driver functionality


## File Structure
- It is recommended to use the [`littlefs`](https://github.com/littlefs-project/littlefs) library to create a usable file structure for the device. 
