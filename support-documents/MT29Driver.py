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

# GPIO pins 6-13 used
def readPins():
    RE.low()
    data = str(Pin(13, Pin.IN).value())
    data += str(Pin(12, Pin.IN).value())
    data += str(Pin(11, Pin.IN).value())
    data += str(Pin(10, Pin.IN).value())
    data += str(Pin(9, Pin.IN).value())
    data += str(Pin(8, Pin.IN).value())
    data += str(Pin(7, Pin.IN).value())
    data += str(Pin(6, Pin.IN).value())
    RE.high()
    return int(data, 2)

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
    
def writeCommand(data):
    CLE.high()
    writePins(data)
    CLE.low()
    
def writeAddress(data):
    ALE.high()
    writePins(data)
    ALE.low()

def readID():    
    writeCommand("10010000") #90h
    writeAddress("00000000") #00h
    
    # Wait 60ns, however the print statement is long enough (i think), WHR
    
    # Read from id data
    print("ID: ")
    
    for i in range(5):
        print(hex(readPins()), end=' ')
    print()
    
    # Read ID ONFI
    writeCommand("10010000") #90h
    writeAddress("00100000") #20h
    
    # Wait a bit
    time.sleep(0.00000006)
    # Read from id data
    print("ID: ")
    
    for i in range(4):
        print(bytearray.fromhex(hex(readPins())[2:]).decode("hex"), end='') # TODO: Fix this, it should be ONFI not NFIO
    print()
    
def readParameterPage():
    writeCommand("11101100") #ECh
    writeAddress("00000000") #00h
    
    # Wait 25.12us
    time.sleep(0.0000252)
    for i in range(140):
        print(hex(readPins()), end=' ')
    print()

def status():
    writeCommand("01110000") #70h
    print(bin(readPins()))

def randReadC(columnAddress, length): # Read from column address
    columnAddress = "0000" + columnAddress
    if (int(columnAddress, 2) > 2111): # Max address
        print("Error, cannot be higher than 2111, currently: " + str(int(columnAddress, 2)))
        return
    if (len(columnAddress) != 16):
        print("Address has to be 12 bits, currently:" + str(len(columnAddress) - 4))
        return
    
    writeCommand("00000100") #05h
    writeAddress(columnAddress[8:16])
    writeAddress(columnAddress[0:8])
    writeCommand("11100000") #E0h
    
    # Wait 60ns, however the print statement is long enough (i think), WHR
    print("Data: ")
    for i in range(length): # Read the first 8 bytes idk why
        print(hex(readPins())[2:], end=' ')
    print()
    

def randReadP(columnAddress, pageAddress, blockAddress, length): # LSB of block address controls which plane it is using
    columnAddress = "0000" + columnAddress
    if (int(columnAddress, 2) > 2111): # Max address
        print("Error, cannot be higher than 2111, currently: " + str(int(columnAddress, 2)))
        return
    if (len(columnAddress) != 16):
        print("Column address has to be 12 bits, currently: " + str(len(columnAddress)))
        return
    if (len(pageAddress) != 6):
        print("Page address has to be 6 bits, currently: " + str(len(pageAddress)))
        return
    if (len(blockAddress) != 11):
        print("Page address has to be 11 bits, currently: " + str(len(blockAddress)))
        return
    
    pageBlockAddress = "0000000" + blockAddress + pageAddress
    
    writeCommand("00000100") #05h
    writeAddress(columnAddress[8:16])
    writeAddress(columnAddress[0:8])
    writeAddress(pageBlockAddress[16:24])
    writeAddress(pageBlockAddress[8:16])
    writeAddress(pageBlockAddress[0:8])
    writeCommand("11100000") #E0h
    
    # Wait 60ns, however the print statement is long enough (i think), WHR
    print("Data: ")
    for i in range(length): # Read the first 8 bytes idk why
        print(hex(readPins())[2:], end=' ')
    print()
    
def randWriteC(columnAddress, data):
    columnAddress = "0000" + columnAddress
    if (int(columnAddress, 2) > 2111): # Max address
        print("Error, cannot be higher than 2111, currently: " + str(int(columnAddress, 2)))
        return
    if (len(columnAddress) != 16):
        print("Address has to be 12 bits")
        return
    writeCommand("10000101") #85h
    writeAddress(columnAddress[8:16])
    writeAddress(columnAddress[0:8])
    
    # Wait 70ns minimum, ADL
    time.sleep(0.0000001)
    length = math.floor(len(data) / 8)
    for i in range(length):
        writePins(data[i*8:i*8+8])
    extraBits = len(data) - length * 8
    if (extraBits > 0):
        padding = (8 - extraBits) * "0"
        writePins(data[(length-1)*8:] + padding)
    
def eraseBlock(rowAddress): # TODO: Row address should just be the block address + page address?, so what randReadP uses?
    writeCommand("01100000") #60h
    writeAddress(rowAddress[16:24])
    writeAddress(rowAddress[8:16])
    writeAddress(rowAddress[0:8])
    writeCommand("11010000") #D0h
    
    # Max wait time 3ms (typ 0.7ms), TODO: use status to determine if it is finished?
    time.sleep(0.003)


def initialise():
    print("Initialising")
    CE.low()
    RE.high()
    WE.high()
    
    ALE.low()
    CLE.low()
    
    WP.high() # Disable write protect for now
        
    # Reset
    writeCommand("11111111")
    time.sleep(0.001) # 1ms max wait time for reset
    
    print("Initialised")

time.sleep(0.0001) #100us max start time
initialise()
time.sleep(0.0000001)
readID()
time.sleep(0.0000001)
status()
time.sleep(0.0000001)
readParameterPage()
time.sleep(0.0000001)
randReadP("000000000000", "000000", "00000000000", 12)
time.sleep(0.1)
randReadC("000000000000", 12)
time.sleep(0.1)
randReadC("000000000000", 12)
time.sleep(0.1)
eraseBlock("0000000000000000000000000000000")
randWriteC("000000000000", "010010000110010101101100011011000110111100100000010101110110111101110010011011000110010000100001") # Hello World!
# 48 65 6C 6C 6F 20 57 6F 72 6C 64 21 hexadecimal
status()
time.sleep(0.1)
status()
randReadC("000000000000", 12)
time.sleep(0.1)
randReadP("000000000000", "000000", "00000000000", 12)
time.sleep(0.1)
randReadC("000000000000", 12)
time.sleep(0.1)

# Must reset command when rebooting device