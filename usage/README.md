# Hardware

To use the chip in a hardware setting, simply take the Altium files found in [`/pcb/altium`](https://github.com/PerthAerospaceStudentTeam/past-storage/blob/main/pcb/altium), and place them in the desired project.

The pinouts are as follow

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

# Software

TBD
