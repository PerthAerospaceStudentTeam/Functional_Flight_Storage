# WT29 Driver For FFS - PAST
# Written by Raphael Ho

from machine import Pin
import time, math

CLE = Pin(14, Pin.OUT)
ALE = Pin(15, Pin.OUT)

RE = Pin(16, Pin.OUT) # Active low
CE = Pin(17, Pin.OUT) # Active low

WE = Pin(18, Pin.OUT) # Active low

WP = Pin(19, Pin.OUT) # Active low

#-----------------------------------------HELPER FUNCTIONS-----------------------------------------------------------------------

def toByte(value):
    value = bin(value)[2:]
    return "0" * (8 - len(value)) + value

def stringToByte(string):
    return "".join([toByte(ord(x)) for x in string])

def verifyColumnAddress(columnAddress):
    if (int(columnAddress, 2) > 2111): # Max address
        print("Error, cannot be higher than 2111, currently: " + str(int(columnAddress, 2)))
        return False
    if (len(columnAddress) != 16):
        print("Column address has to be 12 bits, currently: " + str(len(columnAddress) - 4))
        return False
    return True

def verifyAddress(columnAddress, pageAddress, blockAddress):
    if (not verifyColumnAddress(columnAddress)):
        return False
    if (len(pageAddress) != 6):
        print("Page address has to be 6 bits, currently: " + str(len(pageAddress)))
        return False
    if (len(blockAddress) != 11):
        print("Block address has to be 11 bits, currently: " + str(len(blockAddress)))
        return False
    return True

#-----------------------------------------RAW OPERATIONS-----------------------------------------------------------------------
import rp2
from rp2 import PIO, StateMachine, asm_pio

@asm_pio(sideset_init=PIO.OUT_HIGH, set_init=(rp2.PIO.IN_LOW,) * 8)
def paral_read():
    nop()         .side(0)
    in_(pins, 8)
    push()        .side(1)

read_sm = StateMachine(1, paral_read, freq=90000, sideset_base=RE, in_base=Pin(6))

def setPins():
    Pin(13, Pin.IN, Pin.PULL_DOWN)
    Pin(12, Pin.IN, Pin.PULL_DOWN)
    Pin(11, Pin.IN, Pin.PULL_DOWN)
    Pin(10, Pin.IN, Pin.PULL_DOWN)
    Pin(9, Pin.IN, Pin.PULL_DOWN)
    Pin(8, Pin.IN, Pin.PULL_DOWN)
    Pin(7, Pin.IN, Pin.PULL_DOWN)
    Pin(6, Pin.IN, Pin.PULL_DOWN)

def readRaw():
    data = read_sm.get()
#     data = str(Pin(13, Pin.IN, Pin.PULL_DOWN).value())
#     data += str(Pin(12, Pin.IN, Pin.PULL_DOWN).value())
#     data += str(Pin(11, Pin.IN, Pin.PULL_DOWN).value())
#     data += str(Pin(10, Pin.IN, Pin.PULL_DOWN).value())
#     data += str(Pin(9, Pin.IN, Pin.PULL_DOWN).value())
#     data += str(Pin(8, Pin.IN, Pin.PULL_DOWN).value())
#     data += str(Pin(7, Pin.IN, Pin.PULL_DOWN).value())
#     data += str(Pin(6, Pin.IN, Pin.PULL_DOWN).value())
    return data

def readPins():
    #RE.low()
    read_sm.active(1)
    data = readRaw()
    read_sm.active(0)
    #RE.high()
    return data

# @asm_pio(sideset_init=PIO.OUT_HIGH, out_init=(rp2.PIO.OUT_LOW,) * 8, out_shiftdir=PIO.SHIFT_RIGHT)
# def paral_write():
#     set(pindirs, 0)
#     pull() # Pull data from the pins, will stall and wait for the main program to give data
#     set(pindirs, 1) .side(0)
#     out(pins, 8) # Tells where to send it, and outputs 8 bits
#     nop()           .side(1)
# write_sm = StateMachine(0, paral_write, freq=100000, sideset_base=WE, in_base=Pin(6))

def writePins(data):
    WE.low()
    Pin(13, Pin.OUT).value(int(data[0]))
    Pin(12, Pin.OUT).value(int(data[1]))
    Pin(11, Pin.OUT).value(int(data[2]))
    Pin(10, Pin.OUT).value(int(data[3]))
    Pin(9, Pin.OUT).value(int(data[4]))
    Pin(8, Pin.OUT).value(int(data[5]))
    Pin(7, Pin.OUT).value(int(data[6]))
    Pin(6, Pin.OUT).value(int(data[7]))
    WE.high()
#     write_sm.active(1)
#     write_sm.put(int(data, 2))
#     write_sm.active(0)
    
def writeCommand(data):
    CLE.high()
    writePins(data)
    CLE.low()
    
def writeAddress(data):
    ALE.high()
    writePins(data)
    ALE.low()

#-----------------------------------------FUNCTIONS-----------------------------------------------------------------------

def reset():
    writeCommand("11111111") #FFh
    # wait 5us (tRST)
    time.sleep_us(5)

def readID():    
    writeCommand("10010000") #90h
    writeAddress("00000000") #00h
    
    setPins()
    # Wait 60ns, however the print statement is long enough (i think), WHR
    
    # Read from id data
    print("-----------------------------------------")
    print("ID: ")
    for i in range(5):
        print(hex(readPins())[2:], end=' ')
    print()
    
    # Read ID ONFI
    writeCommand("10010000") #90h
    writeAddress("00100000") #20h
    
    setPins()
    # Wait 60ns (tWHR)
    time.sleep_us(int(0.06))
    # Read from id data
    print("ONFI ID: ")
    for i in range(6):
        try:
            print(bytearray.fromhex(hex(readPins())[2:]).decode("hex"), end='')
        except:
            pass
    print()

    
def readParameterPage(length):
    writeCommand("11101100") #ECh
    writeAddress("00000000") #00h
    
    setPins()
    # Wait 25.12us
    time.sleep_us(int(25.12))
    
    #readPins() # Pre-set the pins to read
    for i in range(length):
        print(hex(readPins())[2:], end=' ')
    print()

def setFeatures(featureAddress, value): #01h, 80h, 81h, 90h are the valid features, TODO: restrict reserved bits
    writeCommand("11101111") #EFh
    writeAddress(featureAddress)
    # Wait minimum 70ns
    writePins(value)
    writePins("00000000")
    writePins("00000000")
    writePins("00000000")
    # Wait 100ns + 1us (tWB+tFEAT) = 1.1us or use status to monitor or R/B
    time.sleep_us(int(1.1))
    if (value == "00000001"):
        time.sleep_ms(1) # Should be long enough (tITC isn't defined)
    
def getFeatures(featureAddress): #01h, 80h, 81h, 90h are the valid features
    writeCommand("11101110") #EEh
    writeAddress(featureAddress)
    
    setPins()
    # Wait minimum 20ns + 1us + 100ns (tRR + tFEAT + tWB) = 1.12us or use status to monitor - must write 00h after to enable data output, or use R/B# rising edge + tRR
    time.sleep_us(int(1.12))
    print("-----------------------------------------")
    print(hex(readPins())[2:])
    for i in range(3):
        readPins() # Reserved output, useless so we discard

def status():
    writeCommand("01110000") #70h
    # Wait 60 ns
    setPins()
    data = toByte(readPins())
    print("-----------------------------------------")
    print(data)
    print("Status: ")
    print("	Write protected" if data[0] == "0" else "	Not write protected")
    print("	Busy" if data[1] == "0" else "	Ready")
    print("	Normal / Uncorrectable (Page read)" if data[4] == "0" else "	Rewrite recommended")
    print("	Success" if data[7] == "0" else "	Fail")

#-----------------------------------------COLUMN ADDRESS OPERATIONS-------------------------------------------------------------

def columnRandReadC(columnAddress, length): # Read from column address
    columnAddress = "0000" + columnAddress
    if (not verifyColumnAddress(columnAddress)):
        return
    
    writeCommand("00000101") #05h
    writeAddress(columnAddress[8:16])
    writeAddress(columnAddress[0:8])
    writeCommand("11100000") #E0h
    
    setPins()
    # Wait 60ns, however the print statement is long enough (i think), WHR
    data = ""
    for i in range(length):
        d = hex(readPins())[2:]
        if (len(d) == 1):
            d = "0" + d
        data += d
    return data
    

def columnRandReadP(columnAddress, pageAddress, blockAddress, length): # LSB of block address controls which plane it is using
    columnAddress = "0000" + columnAddress
    if (not verifyAddress(columnAddress, pageAddress, blockAddress)):
        return
    
    pageBlockAddress = "0000000" + blockAddress + pageAddress
    
    writeCommand("00000110") #06h
    writeAddress(columnAddress[8:16])
    writeAddress(columnAddress[0:8])
    writeAddress(pageBlockAddress[16:24])
    writeAddress(pageBlockAddress[8:16])
    writeAddress(pageBlockAddress[0:8])
    writeCommand("11100000") #E0h
    
    setPins()
    # Wait 60ns, however the print statement is long enough (i think), WHR
    data = ""
    for i in range(length):
        d = hex(readPins())[2:]
        if (len(d) == 1):
            d = "0" + d
        data += d
    return data
    
def columnRandInput(columnAddress, data):
    columnAddress = "0000" + columnAddress
    if (not verifyColumnAddress(columnAddress)):
        return
    writeCommand("10000101") #85h
    writeAddress(columnAddress[8:16])
    writeAddress(columnAddress[0:8])
    
    # Wait 70ns minimum, ADL
    time.sleep_us(int(0.07))
    length = math.floor(len(data) / 8)
    for i in range(length):
        writePins(data[i*8:i*8+8])
    extraBits = len(data) - length * 8
    if (extraBits > 0):
        padding = (8 - extraBits) * "0"
        writePins(data[(length-1)*8:] + padding)
    
    # TODO: wait some time
    status()

#-----------------------------------------READ OPERATIONS-----------------------------------------------------------------------
def readMode():
    writeCommand("00000000") #00h
    
def readPage(columnAddress, pageAddress, blockAddress, length, ecc=False):
    columnAddress = "0000" + columnAddress
    if (not verifyAddress(columnAddress, pageAddress, blockAddress)):
        return
    
    pageBlockAddress = "0000000" + blockAddress + pageAddress
    
    readMode()
    writeAddress(columnAddress[8:16])
    writeAddress(columnAddress[0:8])
    writeAddress(pageBlockAddress[16:24])
    writeAddress(pageBlockAddress[8:16])
    writeAddress(pageBlockAddress[0:8])
    writeCommand("00110000") #30h
    
    setPins()
    # Wait 100ns (tWB)
    time.sleep_us(int(0.1))
    if (ecc): # Wait 70us (tR_ECC) with ecc
        status()
        time.sleep_us(70)
    else:
        # Wait 25us (tR) if no ecc
        time.sleep_us(25)
        
    time.sleep_us(int(0.02)) # Wait 20ns (tRR)
    data = ""
    for i in range(length):
        d = hex(readPins())[2:]
        if (len(d) == 1):
            d = "0" + d
        data += d
    return data
    
def readPageCacheSequential(columnAddress, pageAddress, blockAddress, length, pages, ecc=False, end=True):
    readPage(columnAddress, pageAddress, blockAddress, 0, ecc)
    # Wait 100ns (tWB)
    time.sleep_us(int(0.1))
    if (ecc): # Wait 70us (tR_ECC) with ecc
        status()
        time.sleep_us(70)
    else:
        # Wait 25us (tR) if no ecc
        time.sleep_us(25)
        
    time.sleep_us(int(0.02)) # Wait 20ns (tRR)
    return readPageCacheSequentialContinued(length, pages, ecc, end)
    
def readPageCacheSequentialContinued(length, pages, ecc=False, end=False):
    data = ""
    if (end):
        pages -= 1
    for i in range(pages):
        writeCommand("00110001") #31h
        
        setPins()
        # Wait 100ns (tWB)
        # Wait max 25us (tRCBSY)
        # Wait 20ns (tRR)
        time.sleep_us(int(25.12))
        print(str(i) + "/" + str(pages))
        for j in range(length):
            d = hex(readPins())[2:]
            if (len(d) == 1):
                d = "0" + d
            data += d
    if (end):
        print(str(pages) + "/" + str(pages))
        data += readPageCacheLast(length)
    return data

def readPageCacheLast(length):
    writeCommand("00111111") #3Fh
    setPins()
    data = ""
    # Wait 100ns (tWB)
    # Wait max 25us (tRCBSY)
    # Wait 20ns (tRR)
    time.sleep_us(int(25.12))
    for j in range(length):
        d = hex(readPins())[2:]
        if (len(d) == 1):
            d = "0" + d
        data += d
    return data
#-----------------------------------------PROGRAM OPERATIONS-----------------------------------------------------------------------

def programPage(columnAddress, pageAddress, blockAddress, data):
    columnAddress = "0000" + columnAddress
    if (not verifyAddress(columnAddress, pageAddress, blockAddress)):
        return
    
    pageBlockAddress = "0000000" + blockAddress + pageAddress
    
    writeCommand("10000000") #80h
    writeAddress(columnAddress[8:16])
    writeAddress(columnAddress[0:8])
    writeAddress(pageBlockAddress[16:24])
    writeAddress(pageBlockAddress[8:16])
    writeAddress(pageBlockAddress[0:8])
    
    # Wait 70ns minimum, ADL
    time.sleep_us(int(0.07))
    length = math.floor(len(data) / 8)
    for i in range(length):
        writePins(data[i*8:i*8+8])
    extraBits = len(data) - length * 8
    if (extraBits > 0):
        padding = (8 - extraBits) * "0"
        writePins(data[(length-1)*8:] + padding)
    
    writeCommand("00010000") #10h

    # Wait 100ns + max 600us (tWB + tPROG & tPROG_ECC)
    time.sleep_us(int(600.1))
    # Must check status after each write
    status()

def programPageString(columnAddress, pageAddress, blockAddress, data):
    columnAddress = "0000" + columnAddress
    if (not verifyAddress(columnAddress, pageAddress, blockAddress)):
        return
    
    pageBlockAddress = "0000000" + blockAddress + pageAddress
    
    writeCommand("10000000") #80h
    writeAddress(columnAddress[8:16])
    writeAddress(columnAddress[0:8])
    writeAddress(pageBlockAddress[16:24])
    writeAddress(pageBlockAddress[8:16])
    writeAddress(pageBlockAddress[0:8])
    
    # Wait 70ns minimum, ADL
    time.sleep_us(int(0.07))
    for i in range(len(data)):
        writePins(stringToByte(data[i]))
    
    writeCommand("00010000") #10h

    # Wait 100ns + max 600us (tWB + tPROG & tPROG_ECC)
    time.sleep_us(int(600.1))
    # Must check status after each write
    status()

#-----------------------------------------ERASE OPERATIONS-----------------------------------------------------------------------

def eraseBlock(pageAddress, blockAddress):
    if (not verifyAddress("0000000000000000", pageAddress, blockAddress)):
        return
    
    pageBlockAddress = "0000000" + blockAddress + pageAddress
    
    writeCommand("01100000") #60h
    writeAddress(pageBlockAddress[16:24])
    writeAddress(pageBlockAddress[8:16])
    writeAddress(pageBlockAddress[0:8])
    writeCommand("11010000") #D0h
    
    # Max wait time 3ms (typ 0.7ms), TODO: use status to determine if it is finished
    time.sleep_ms(3)
    status()

def initialise():
    print("Initialising")
    CE.low()
    RE.high()
    WE.high()
    
    ALE.low()
    CLE.low()
    
    WP.high() # Disable write protect for now
    #read_sm.active(1)
    
    # Reset
    reset()
    time.sleep_ms(1) # 1ms max wait time for first reset
    
    print("Initialised")