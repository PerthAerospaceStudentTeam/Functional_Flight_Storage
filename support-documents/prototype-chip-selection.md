# Overview

There are many chips that can be used for storage. All are to be automotive grade, preferably aerospace grade This project will focus on the following 3:

## NAND Flash

On paper, the most desirable form of memory. It is non-volatile, high capacity, and cheaper. The downsides are the limited amount of write cycles - this could prove fatal in a mission critical environment

[Chip 1](https://au.mouser.com/ProductDetail/Winbond/W25N01GVSFIG?qs=qSfuJ%2Bfl%2Fd5wRcUOkRc5Cw%3D%3D)

- SPI, 25mA

### Reasons for selection

- Used by Binar
- Low cost to storage space
- Easy to interface with

### Reasons for not using

- (Relatively) High current consumption

[Chip 2](https://au.mouser.com/ProductDetail/Micron/MT29F2G08ABAEAWP-AATXE-TR?qs=j%252B1pi9TdxUaMl26HJ%252Bo32A%3D%3D)

- Parallel, 35mA, typ 25mA

### Reasons for selection

- Automotive grade

### Reasons for not using

- Needs a LOT of GPIO pins
- Expensive

## NOR Flash

Similar to NOR flash but with much higher read/write speeds. Costs more

[Chip 1](https://au.mouser.com/ProductDetail/Renesas-Dialog/AT25EU0081A-SSUN-T?qs=HoCaDK9Nz5cZm9CJYdZrgw%3D%3D)

- SPI, 3mA, typ 1.6mA

### Reasons for selection

- VERY low current consumption
- Very high read/write rates

### Reasons for not using

- Not high storage capacity (may be good as a bootloader for firmware?)
