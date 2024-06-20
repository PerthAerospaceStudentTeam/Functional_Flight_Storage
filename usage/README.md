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

## File Structure
- It is recommended to use the [`littlefs`](https://github.com/littlefs-project/littlefs) library to create a usable file structure for the device. 
