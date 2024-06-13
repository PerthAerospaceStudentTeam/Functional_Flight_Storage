# Flash Storage For FFS - PAST
# Written by Raphael Ho

from ONFIDriver import *
import time

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
        value = hex_to_byte(int(input("Value: "), 16))
        if option == 1:
            getFeatures(hex_to_byte(int(0x01, 16)), value)
        elif option == 2:
            getFeatures(hex_to_byte(int(0x80, 16)), value)
        elif option == 3:
            getFeatures(hex_to_byte(int(0x81, 16)), value)
        elif option == 4:
            getFeatures(hex_to_byte(int(0x90, 16)), value)
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
            setFeatures(hex_to_byte(int(0x01, 16)))
        elif option == 2:
            setFeatures(hex_to_byte(int(0x80, 16)))
        elif option == 3:
            setFeatures(hex_to_byte(int(0x81, 16)))
        elif option == 4:
            setFeatures(hex_to_byte(int(0x90, 16)))
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
            d = string_to_byte(input("Data (String): "))
        programPage(caddr, paddr, baddr, d)
    elif action == 9:
        paddr = input("pageAddress: ")
        baddr = input("blockAddress: ")
        eraseBlock(paddr, baddr)
    else:
        print("Unknown action, try again")

print(readPage("000000000000", "000000", "00010000010", 50))
#eraseBlock("000000", "00010000010")
time.sleep(0.1)
#programPage("000000000000", "000000", "00010000010", string_to_byte("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut tempus eros quis felis scelerisque, nec auctor elit venenatis. Maecenas ultrices arcu sed urna ullamcorper, at malesuada enim sollicitudin. Donec blandit mauris magna, vitae pharetra risus pretium at. Mauris sapien justo, consectetur ut dignissim eu, rutrum a elit. Sed diam ipsum, elementum at augue ut, vehicula pulvinar arcu. Nullam at elit elementum, mattis purus non, aliquam nisi. Nullam ut risus sed eros gravida laoreet. Nunc finibus, purus eget convallis congue, eros felis rhoncus velit, et ultrices risus purus ac massa. Curabitur eu maximus odio.\nQuisque eu leo sagittis odio sollicitudin aliquam non sed lacus. Pellentesque ut auctor metus. Nulla eu diam rutrum, scelerisque odio non, interdum lectus. Nunc viverra sed quam sed malesuada. Morbi blandit mi metus, at varius magna dictum a. Ut pulvinar convallis nibh, lacinia egestas augue sodales eu. Duis egestas, metus nec faucibus rutrum, urna mi dapibus ante, non pharetra felis metus ac elit."))
print(readPage("000000000000", "000000", "00010000010", 2000))
f = open("dump.txt", "w")
t1 = time.time()
f.write(readPageCacheSequential("000000000000", "000000", "00010000010", 1056, 16))
t2 = time.time()
f.close()
print(str(t2 - t1))