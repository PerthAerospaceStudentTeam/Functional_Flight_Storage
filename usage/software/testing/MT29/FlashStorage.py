# Flash Storage For FFS - PAST
# Written by Raphael Ho
import rp2

from ONFIDriverParallel import *
import time

############################ Functions ##################################################

def readBlockData(filename, blockAddr):
    f = open(filename, "w")
    maxChar = 2112

    t1 = time.ticks_ms()
    f.write(readPageCacheSequential("000000000000", "000000", blockAddr, maxChar, 8))
    f.write(readPageCacheSequential("000000000000", "001000", blockAddr, maxChar, 8))
    f.write(readPageCacheSequential("000000000000", "010000", blockAddr, maxChar, 8))
    f.write(readPageCacheSequential("000000000000", "011000", blockAddr, maxChar, 8))
    f.write(readPageCacheSequential("000000000000", "100000", blockAddr, maxChar, 8))
    f.write(readPageCacheSequential("000000000000", "101000", blockAddr, maxChar, 8))
    f.write(readPageCacheSequential("000000000000", "110000", blockAddr, maxChar, 8))
    f.write(readPageCacheSequential("000000000000", "111000", blockAddr, maxChar, 8))
    t2 = time.ticks_ms()
    f.close()
    print(str((t2 - t1) / 1000))

def writeBlockData(filename, blockAddr):
    f1 = open(filename, "r")
    t1 = time.ticks_ms()
    
    page = 0
    maxChar = 2112
    lineSum = ""

    for line in f1:
        lineSum += line
        while(len(lineSum) > maxChar):
            value = bin(page)[2:]
            programPageString("000000000000", "0" * (6 - len(value)) + value, blockAddr, lineSum[:maxChar])
            print(page)
            lineSum = lineSum[maxChar:]
            
            page += 1
    if (len(lineSum) > 0):
        value = bin(page)[2:]
        programPageString("000000000000", "0" * (6 - len(value)) + value, blockAddr, lineSum)
    print(page)
    t2 = time.ticks_ms()
    f1.close()
    print(str((t2 - t1) / 1000))

############################ PROGRAM ##################################################

time.sleep(0.0001) #100us max start time
initialise() # Must reset command when rebooting device
readID()
status()
#setFeatures("10010000", "00001000") # Turn on ECC
#getFeatures("10010000")

# Read page, then you can use random data read and random data input the modify the data in the cache registers

end = False
while (not end):
    print("""FLASH STORAGE PROGRAM
Written by Raphael Ho for FFS - Perth Aerospace Student Team
Actions:
    0. Exit
    1. Reset
    2. Read ID
    3. Read parameter page
    4. Set features
    5. Get features
    6. Get status
    7. Read page
    8. Program page
    9. Erase block
    10. Block commands
""")
    action = int(input("Action: "))
    if action == 0:
        end = True
    elif action == 1:
        reset()
    elif action == 2:
        readID()
    elif action == 3:
        length = int(input("How long? (120 recommended) "))
        readParameterPage(length)
    elif action == 4:
        print("""Valid features:
    1. 01h Timing mode
    2. 80h Programmable output drive strength
    3. 81h Programmable RB# pull-down strength
    4. 90h Array operation mode
""")
        option = int(input("Choose 1-4: "))
        value = toByte(int(input("Value: "), 16))
        if option == 1:
            setFeatures(toByte(0x01), value)
        elif option == 2:
            setFeatures(toByte(0x80), value)
        elif option == 3:
            setFeatures(toByte(0x81), value)
        elif option == 4:
            setFeatures(toByte(0x90), value)
        else:
            print("Option unknown")
    elif action == 5:
        print("""Valid features:
    1. 01h Timing mode
    2. 80h Programmable output drive strength
    3. 81h Programmable RB# pull-down strength
    4. 90h Array operation mode
""")
        option = int(input("Choose 1-4: "))
        if option == 1:
            getFeatures(toByte(0x01))
        elif option == 2:
            getFeatures(toByte(0x80))
        elif option == 3:
            getFeatures(toByte(0x81))
        elif option == 4:
            getFeatures(toByte(0x90))
        else:
            print("Option unknown")
    elif action == 6:
        status()
    elif action == 7:
        caddr = input("columnAddress: ")
        paddr = input("pageAddress: ")
        baddr = input("blockAddress: ")
        length = int(input("Length: "))
        print(readPage(caddr, paddr, baddr, length))
    elif action == 8:
        caddr = input("columnAddress: ")
        paddr = input("pageAddress: ")
        baddr = input("blockAddress: ")
        print("""Data formats:
1. Raw binary
2. String""")
        f = int(input("Data format: "))
        d = ""
        if f == 1:
            d = input("Data (Binary): ")
        elif f == 2:
            d = stringToByte(input("Data (String): "))
        programPage(caddr, paddr, baddr, d)
    elif action == 9:
        paddr = input("pageAddress: ")
        baddr = input("blockAddress: ")
        eraseBlock(paddr, baddr)
    elif action == 10:
        baddr = input("blockAddress: ")
        f = input("Filename: ")
        option = int(input("""1. Write
2. Read
"""))
        if option == 1:
            writeBlockData(f, baddr)
        else:
            readBlockData(f, baddr)
    else:
        print("Unknown action, try again")

#print(readPage("000000000000", "000000", "00010000010", 50))
#eraseBlock("000000", "00000000010")
#eraseBlock("000000", "00000000011")

#eraseBlock("000000", "00000000001")
#writeBlockData("data.txt", "00000000001")
#readBlockData("dump.txt", "00000000001")


#programPage("000000000000", "000000", "00010000010", stringToByte("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut tempus eros quis felis scelerisque, nec auctor elit venenatis. Maecenas ultrices arcu sed urna ullamcorper, at malesuada enim sollicitudin. Donec blandit mauris magna, vitae pharetra risus pretium at. Mauris sapien justo, consectetur ut dignissim eu, rutrum a elit. Sed diam ipsum, elementum at augue ut, vehicula pulvinar arcu. Nullam at elit elementum, mattis purus non, aliquam nisi. Nullam ut risus sed eros gravida laoreet. Nunc finibus, purus eget convallis congue, eros felis rhoncus velit, et ultrices risus purus ac massa. Curabitur eu maximus odio.\nQuisque eu leo sagittis odio sollicitudin aliquam non sed lacus. Pellentesque ut auctor metus. Nulla eu diam rutrum, scelerisque odio non, interdum lectus. Nunc viverra sed quam sed malesuada. Morbi blandit mi metus, at varius magna dictum a. Ut pulvinar convallis nibh, lacinia egestas augue sodales eu. Duis egestas, metus nec faucibus rutrum, urna mi dapibus ante, non pharetra felis metus ac elit."))
#data = ""
#programPage("000000000000", "000000", "00000000001", data)