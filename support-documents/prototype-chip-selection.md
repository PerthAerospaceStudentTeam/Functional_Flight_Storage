# Overview

There are many chips that can be used for storage. All are to be automotive grade, preferably aerospace grade This project will focus on the following 3:

## NAND Flash

On paper, the most desirable form of memory. It is non-volatile, high capacity, and cheaper. The downsides are the limited amount of write cycles - this could prove fatal in a mission critical environment
https://au.mouser.com/ProductDetail/Winbond/W25N01GVSFIG?qs=qSfuJ%2Bfl%2Fd5wRcUOkRc5Cw%3D%3D
- SPI, 25mA

https://au.mouser.com/datasheet/2/671/MICT_S_A0003602039_1-2574397.pdf
- https://au.mouser.com/pdfDocs/micron_stmicroelectronics_compatibility_guide3.pdf
- Parallel, 35mA, typ 25mA

## NOR Flash

Similar to NOR flash but with much higher read/write speeds. Costs more

## eMMC

Very high capacity storage which acts very similar to an SD card. However, we might not need this much storage so chips could be redundant
https://au.mouser.com/datasheet/2/615/EM_30_fact_sheet-2853778.pdf
- ~100mA
