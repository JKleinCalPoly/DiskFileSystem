import TinyFS 
from TinyFS import *

if __name__ == '__main__':

    disk_store = tfs_mkfs(DEFAULT_DISK_NAME, DEFAULT_DISK_SIZE) #diskFile object returned by LibDisk.open()
    file_system = tfs_mount(DEFAULT_DISK_NAME) #same diskFile object, but opened
    print("This is our SuperBlock at initialization")
    print(LibDisk.readBlock(file_system, 0))

    try:
        try_file = tfs_open("name_too_long.txt")
    except TinyFSNameError as e:
        print(e.message)

    a_file = tfs_open("a.txt")
    b_file = tfs_open("b.txt")

    print(ResourceTable)

    in1 = "filler data for first file"
    tfs_write(a_file, in1)
    for i in range(len(in1)):
        print(tfs_readByte(a_file), end="")
    print("\n")

    in2 = "different data for a different file"
    tfs_write(b_file, in2)
    for i in range(len(in2)):
        print(tfs_readByte(b_file), end="")
    print("\n")
    tfs_close(a_file)
    try:
        for i in range(len(in1)):
            print(tfs_readByte(a_file), end="")
    except TinyFSFileNotFoundError as e:
        print(e.message)

    a_file = tfs_open("a.txt")
    for i in range(len(in1)):
        print(tfs_readByte(a_file), end="")
    print("\n")
    print(ResourceTable)

    tfs_unmount(file_system)
    print("remounting, clearing resource table")
    file_system = tfs_mount(DEFAULT_DISK_NAME)
    print(ResourceTable)
    a_file = tfs_open("a.txt")
    print(ResourceTable)
    for i in range(len(in1)):
        print(tfs_readByte(a_file), end="")
    print("\n\n")

    print(LibDisk.readBlock(file_system, 0))

    in1 = "THIS IS A LOT MORE TEXT SO THAT WE HIT THE NEXT BLOCK AND HAVE TO ALLOCATE AND PAGE. I DONT KNOW WHAT ELSE TO PUT SO HAVE SOME 7s. ACTUALY I GUESS THAT DOESN'T WORK VERY WELL SINCE I'D LIKE TO BE ABLE TO SEE IF ANY CHARACTERS ARE MISSING SO I KEPT WRITING. THIS SHOULD DEFINITELY BE IN THE NEXT BLOCK BY NOW SO I'LL STOP."
    tfs_write(a_file, in1)
    for i in range(len(in1)):
        print(tfs_readByte(a_file), end="")
    print("\n")
    print(LibDisk.readBlock(file_system, 0))

    tfs_readdir()
    b_file = tfs_open("b.txt")
    tfs_delete(b_file)

    try:
        for i in range(len(in2)):
            print(tfs_readByte(b_file), end="")
    except TinyFSFileNotFoundError as e:
        print(e.message)
    tfs_readdir()
    print("\n")

    tfs_seek(a_file, 0)
    for i in range(15):
        if i == 4 or i == 7:
            tfs_writeByte(a_file, "_")
            tfs_seek(a_file, -1)
        print(tfs_readByte(a_file), end="")
    print("")

    print("skipping ahead 15 characters")
    tfs_seek(a_file, 30)
    for i in range(15):
        print(tfs_readByte(a_file), end="")
    print("\n")
    
    c_file = tfs_open("c.txt")
    in3 = "some sample text for a 3rd file"
    tfs_write(c_file, in3)
    for i in range(len(in3)):
        print(tfs_readByte(c_file), end="")
    print("\n")
    tfs_makeRO(c_file)
    tfs_write(c_file, "new data")
    tfs_makeRW(c_file)

    in4 = "new data"
    tfs_write(c_file, in4)
    print(ResourceTable[c_file])
    for i in range(len(in4)):
        print(tfs_readByte(c_file), end="")
    print("\n")

    tfs_readdir()
    tfs_rename(c_file, "c2.img")
    print("changing name:")
    tfs_readdir()