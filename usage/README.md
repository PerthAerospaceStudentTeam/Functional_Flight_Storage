# Hardware

To use the chip in a hardware setting, simply take the Altium files found in [`/pcb/altium`](https://github.com/PerthAerospaceStudentTeam/past-storage/blob/main/pcb/altium), and place them in the desired project.

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

The pinouts for the parallel interface are as follows
| Pin  | Connect | Use                                                                                                |
| ---- | ------- | -------------------------------------------------------------------------------------------------- |
| +3v3 | +3v3    | Provide power to the board                                                                         |
| GND  | GND     | Provide ground to the board                                                                        |
| CLK  | CLK     | Provides the clock signal - can be connected to external clock provided it is shared between chips |
| WP#  | WP#   | Write Protect active low - Pulled low |
| WE#  | WE#   | Write Enable active low |
| AL   | AL    | Address Latch Enable - Load address from IO into address register |
| CL   | CL    | Command Latch Enable - Load address from IO into command register |
| CE#  | CE#   | Chip enable active low - Pulled high |
| RE#  | RE#   | Read enable active low - Pulled high |
| RB#  | RB#   | Ready/Busy active low - Pulled up |
| IO0  | IO0   | Data I/O                                                                |
| IO1  | IO1   | Data I/O                                                                |
| IO2  | IO2   | Data I/O                                                                |
| IO3  | IO3   | Data I/O                                                                |
| IO4  | IO4   | Data I/O                                                                |
| IO5  | IO5   | Data I/O                                                                |
| IO6  | IO6   | Data I/O                                                                |
| IO7  | IO7   | Data I/O                                                                |

# Software

TBD
