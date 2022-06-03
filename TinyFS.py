import math

import LibDisk
from LibDisk import *
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"
MAX_DATA_IN_BLOCK = BLOCKSIZE - 2
BLOCK_ONE_METADATA_SIZE = 9

ResourceTable = {} #format {FD: [name, index, inode addr, RO?]}
global currentMount
currentMount = None
global fdIndex
fdIndex = 1

# Makes an empty TinyFS file system of size nBytes on the file specified by ‘filename’.
#This function should use the emulated disk library to open the specified file, and upon success, format the file to be mountable. 
#This includes initializing all data to 0x00, setting magic numbers, initializing and writing the superblock and other metadata, etc. 
#Must return a specified success/error code. */
def tfs_mkfs(filename, nBytes):
    disk = LibDisk.openDisk(filename, nBytes)
    for i in range(int(nBytes / LibDisk.BLOCKSIZE)):
        if i == 0:
            LibDisk.writeBlock(disk, i, "5A00010001E0")
            #'5A':magic number, '0001':addr of root inode
            #'0001':set root inode as active
            #'E0':mark first 3 blocks as allocated in bitmap
        elif i == 1:
            LibDisk.writeBlock(disk, i, "0002")
        elif i == 2:
            LibDisk.writeBlock(disk, i, "01")
        else:
            LibDisk.writeBlock(disk, i, "00" * LibDisk.BLOCKSIZE)
    LibDisk.closeDisk(disk)
    return disk

#/* tfs_mount(char *filename) “mounts” a TinyFS file system located within ‘filename’.
# tfs_unmount(void) “unmounts” the currently mounted file system. As part of the mount operation,
# tfs_mount should verify the file system is the correct type.#
# Only one file system may be mounted at a time. Use tfs_unmount to cleanly unmount the currently mounted file system.
# Must return a specified success/error code. */
def tfs_mount(filename):
    global currentMount # replace w/ filename of current filesystem
    try:
        if (currentMount != None):
            tfs_unmount(currentMount)
        FD = LibDisk.openDisk(filename, 0)
        currentMount = FD
    except Exception as e:
        print(e)
        exit(-1)

    block = LibDisk.readBlock(FD, 0)
    if not block.startswith("5A"):
        raise DiskFormatError(filename)
    return FD

def tfs_unmount(diskFile):
    LibDisk.closeDisk(diskFile)
    return 0

#/* Opens a file for reading and writing on the currently mounted file system.#
# Creates a dynamic resource table entry for the file (the structure that tracks open files, the internal file pointer, etc.),
# and returns a file descriptor (integer) that can be used to reference this file while the filesystem is mounted. */
def tfs_open(name):
    #read bytes 1-2 of superblock for root inode address
    #read root directory address from root inode bytes 0-1
    #search root directory for 'name'
    #if name not found, allocate inode and first data block for new file
    #"open" file by updating superblock 3-4
    #create resourcetable entry
    #return fd of resource table entry
    global currentMount
    global fdIndex
    namestuff = 8 - len(name)
    if namestuff > 0:
        for i in range(namestuff):
            name += bytes.fromhex("00").decode("ASCII")
        print(name)
    superblock = LibDisk.readBlock(currentMount, 0)
    rootinode = LibDisk.readBlock(currentMount, int(superblock[2:6], 16))
    rootdirectory = LibDisk.readBlock(currentMount, int(rootinode[:4], 16))
    if not rootdirectory.startswith("01"):
        raise DiskFormatError(DEFAULT_DISK_NAME)
    sliceStart = 18
    sliceEnd = 34
    while True:
        entry = rootdirectory[sliceStart:sliceEnd]
        entry = bytes.fromhex(entry).decode("ASCII")
        if entry == name:
            break
        sliceEnd += 20
        sliceStart += 20
        if sliceEnd > 500:
            #print(name + " not found")
            break

    if entry != name:
        sliceStart = 18
        sliceEnd = 34
        while True:
            entry = rootdirectory[sliceStart:sliceEnd]
            if entry == "0000000000000000":
                entry = "".join([hex(ord(x))[2:] for x in name])
                numstuff = 16 - len(entry)
                if numstuff > 0:
                    for i in range (numstuff):
                        entry += "0"

                bitmap = superblock[10:]
                nextInode, bitmap = tfs_alloc(bitmap)
                nextData, bitmap = tfs_alloc(bitmap)
                rootdirectory = rootdirectory[:sliceStart] + entry + format("%04X" % nextInode) + rootdirectory[sliceEnd+4:]
                superblock = superblock[:10] + bitmap
                newInode = format("%04X" % nextData)
                LibDisk.writeBlock(currentMount, nextInode, newInode)
                newData = "00" + entry
                LibDisk.writeBlock(currentMount, nextData, newData)
                break
            sliceEnd += 20
            sliceStart += 20
            if sliceEnd > 500:
                print("no room for " + name)
                break

    fileinode = rootdirectory[sliceEnd:sliceEnd+4]
    #print(fileinode)
    superblock = superblock[0:6] + fileinode + superblock[10:]
    #print(superblock)
    LibDisk.writeBlock(currentMount, 0, superblock)
    LibDisk.writeBlock(currentMount, 2, rootdirectory)
    fd = fdIndex
    fdIndex += 1
    ResourceTable.update({fd:[name, 0, int(fileinode), False]})
    return fd

def tfs_alloc(bitmap):
    for i, c in enumerate(bitmap):
        if c != 'F':
            binr = bin(int(c, 16))[2:].zfill(4)
            #print(binr)
            for j, b in enumerate(binr):
                if b == '0':
                    binr = binr[:j] + '1' + binr[j + 1:]
                    return (i * 4) + j, bitmap[:i] + hex(int(binr, 2))[2:].upper() + bitmap[i+1:]

#/* Closes the file and removes dynamic resource table entry */
def tfs_close(FD):
    if FD in ResourceTable:
        ResourceTable.pop(FD)
    else:
        raise FileNotFoundError(FD)
    return 0
#/* Writes buffer ‘buffer’ of size ‘size’, which represents an entire file’s contents, to the file described by ‘FD’.#
# Sets the file pointer to 0 (the start of file) when done. Returns success/error codes. */
def tfs_write(FD, buffer):
    #check if fd in resourcetable
    #determine number of blocks required for len(buffer) bytes
    #determine current number of blocks of file
    #if current blocks > required blocks: free unneeded blocks
    #else allocate necessary blocks (call alloc, rewrite bitmap to super block)
    #chunk up buffer
    #append next block address to end of each buffer chunk
    #write each buffer chunk to the appropriate block
    #update length in inode
    global currentMount
    if FD not in ResourceTable:
        raise TinyFSFileNotFoundError(FD)
    #numblocks = math.ceil((len(buffer) + BLOCK_ONE_METADATA_SIZE) / MAX_DATA_IN_BLOCK)

    if ResourceTable[FD][3]:
        print("You can't write to a RO file!")
        return -1

    inode = ResourceTable[FD][2]
    fileInode = LibDisk.readBlock(currentMount, inode)
    LibDisk.writeBlock(currentMount, inode, fileInode[:4] + format("%06X" % len(buffer)) + fileInode[10:])
    #lenCurr = int(fileInode[4:10], 16) #parse hex string to decimal
    datablock = int(fileInode[:4], 16)
    #numblocksCurr = math.ceil((lenCurr + BLOCK_ONE_METADATA_SIZE) / MAX_DATA_IN_BLOCK)
    #diffblocks = numblocksCurr - numblocks
    #if diffblocks > 0:
    #    print("dont worry about a thing")
        #do some freeing
    blockList = tfs_get_block_list(datablock)
    blockList.reverse()
    for i, block in enumerate(blockList):
        if i != 0:
            tfs_free_block(block)
    i = 0
    chunks = []
    while i < len(buffer):
        if i == 0:
            chunks.append(buffer[i:MAX_DATA_IN_BLOCK-BLOCK_ONE_METADATA_SIZE])
            i += MAX_DATA_IN_BLOCK-BLOCK_ONE_METADATA_SIZE
        else:
            chunks.append((buffer[i:i+MAX_DATA_IN_BLOCK]))
            i += MAX_DATA_IN_BLOCK
    superblock = LibDisk.readBlock(currentMount, 0)
    bitmap = superblock[10:]
    datablockData = LibDisk.readBlock(currentMount, datablock)
    for i, chunk in enumerate(chunks):
        chunk = "".join([hex(ord(x))[2:] for x in chunk])
        if i == 0:
            chunk = datablockData[:18] + chunk
        if i == len(chunks) - 1:
            while len(chunk) < (MAX_DATA_IN_BLOCK * 2):
                chunk = chunk + '0'
            chunk = chunk + "FFFF"
            LibDisk.writeBlock(currentMount, datablock, chunk)
        else:
            nextblock, bitmap = tfs_alloc(bitmap)
            nextCode = format("%04X" % nextblock)
            chunk += nextCode
            LibDisk.writeBlock(currentMount, datablock, chunk)
            LibDisk.writeBlock(currentMount, 0, superblock[:10] + bitmap)
            datablock = nextblock
    ResourceTable.update({FD: [ResourceTable[FD][0], 0, ResourceTable[FD][2], ResourceTable[FD][3]]})
    return 0

def tfs_free_block(block):
    global currentMount
    superblock = LibDisk.readBlock(currentMount, 0)
    bitmap =  superblock[10:]
    bitmapIndex = block // 4
    bitmapOffset =  block % 4
    current = bitmap[bitmapIndex]
    binr = bin(int(current, 16))[2:].zfill(4)
    binr = binr[:bitmapOffset] + '0' + binr[bitmapOffset+1:]
    superblock = superblock[:10] + bitmap[:bitmapIndex] + hex(int(binr, 2))[2:].upper() + bitmap[bitmapIndex+1:]
    LibDisk.writeBlock(currentMount, 0, superblock)


def tfs_get_block_list(block):
    global currentMount
    data = LibDisk.readBlock(currentMount, block)
    nextBlock = int(data[-4:], 16)
    if nextBlock == 0 or nextBlock == 65535:
        return [block]
    ret = []
    for val in tfs_get_block_list(nextBlock):
        ret.append(val)
    ret.append(block)
    return ret


#/* deletes a file and marks its blocks as free on disk. */
def tfs_delete(FD):

    if FD not in ResourceTable:
        raise TinyFSFileNotFoundError(FD)

    if (ResourceTable[FD][3]):
        print("You can't delete a RO file!")
        return -1

    #get inode from resource table
    #get first data block from inode
    #get data block list
    #free all data blocks and inode from bitmap
    #remove root directory entry
    #remove resource table entry
    rtentry = ResourceTable[FD]
    inode = rtentry[2]
    fileInode = LibDisk.readBlock(currentMount, inode)
    datablock = int(fileInode[:4], 16)
    blockList = tfs_get_block_list(datablock)
    blockList.append(inode)
    for block in blockList:
        tfs_free_block(block)
    namestuff = 8 - len(rtentry[0])
    if namestuff > 0:
        for i in range(namestuff):
            rtentry[0] += bytes.fromhex("00").decode("ASCII")

    superblock = LibDisk.readBlock(currentMount, 0)
    rootinode = LibDisk.readBlock(currentMount, int(superblock[2:6], 16))
    rootdirectory = LibDisk.readBlock(currentMount, int(rootinode[:4], 16))
    if not rootdirectory.startswith("01"):
        raise DiskFormatError(DEFAULT_DISK_NAME)
    sliceStart = 18
    sliceEnd = 34
    while True:
        entry = rootdirectory[sliceStart:sliceEnd]
        entry = bytes.fromhex(entry).decode("ASCII")
        if entry == rtentry[0]:
            break
        sliceEnd += 20
        sliceStart += 20
        if sliceEnd > 500:
            # print(name + " not found")
            break
    rootdirectory = rootdirectory[:sliceStart] + ("0"*16) + rootdirectory[sliceEnd:]
    LibDisk.writeBlock(currentMount, int(rootinode[:4], 16), rootdirectory)
    ResourceTable.pop(FD)
    return 0
#/* reads one byte from the file and copies it to ‘buffer’, using the current file pointer location and incrementing it by one upon success.
# If the file pointer is already at the end of the file then tfs_readByte() should return an error and not increment the file pointer. */
def tfs_readByte(FD):
    if FD not in ResourceTable:
        raise TinyFSFileNotFoundError(FD)
    inode = ResourceTable[FD][2]
    fileInode = LibDisk.readBlock(currentMount, inode)
    length = fileInode[5:10]
    length = int(length, 16)
    if ResourceTable[FD][1] >= length:
        raise TinyFSReadEOFError(FD)
    #calculate the block and block offset
    bOffset = ResourceTable[FD][1]
    bAddr = 0
    cap = MAX_DATA_IN_BLOCK - BLOCK_ONE_METADATA_SIZE
    while bOffset >= cap:
        bOffset -= cap
        if bAddr == 0:
            cap = MAX_DATA_IN_BLOCK
        bAddr += 1
    if bAddr == 0:
        bOffset += 9
    datablock = int(fileInode[:4], 16)
    blockList = tfs_get_block_list(datablock)
    blockList.reverse()
    data = LibDisk.readBlock(currentMount, blockList[bAddr])
    #print(data)
    data = data[bOffset * 2: (bOffset * 2) + 2]
    #print(data + "\n")
    ret = bytes.fromhex(data).decode("ASCII")
    ResourceTable[FD][1] += 1
    return ret

#/* change the file pointer location to offset (absolute). Returns success/error codes.*/
def tfs_seek(FD, offset):
    if FD not in ResourceTable:
        raise TinyFSFileNotFoundError(FD)
    if offset < 0:
        offset += ResourceTable[FD][1] 
        if offset < 0:
            offset = 0

    #check if offset in bounds for file
    #set resource table offset
    ResourceTable[FD] = (ResourceTable[FD][0], offset, ResourceTable[FD][2], ResourceTable[FD][3])

#makes the file read only. If a file is RO, all tfs_write() and tfs_deleteFile()  functions that try to use it fail.
def tfs_makeRO(FD):
    if FD not in ResourceTable:
        raise TinyFSFileNotFoundError(FD)
    ResourceTable[FD] = (ResourceTable[FD][0], ResourceTable[FD][1], ResourceTable[FD][2], True)

#makes the file read-write
def tfs_makeRW(FD):
    if FD not in ResourceTable:
        raise TinyFSFileNotFoundError(FD)
    ResourceTable[FD] = (ResourceTable[FD][0], ResourceTable[FD][1], ResourceTable[FD][2], False)
#a function that can write one byte to an exact position inside the file.
def tfs_writeByte(FD, byte):
    if FD not in ResourceTable:
        raise TinyFSFileNotFoundError(FD)
    inode = ResourceTable[FD][2]
    fileInode = LibDisk.readBlock(currentMount, inode)
    length = fileInode[5:10]
    length = int(length, 16)
    if ResourceTable[FD][1] >= length:
        raise TinyFSReadEOFError(FD)
    # calculate the block and block offset
    bOffset = ResourceTable[FD][1]
    bAddr = 0
    cap = MAX_DATA_IN_BLOCK - BLOCK_ONE_METADATA_SIZE
    while bOffset >= cap:
        bOffset -= cap
        if bAddr == 0:
            cap = MAX_DATA_IN_BLOCK
        bAddr += 1
    if bAddr == 0:
        bOffset += 9
    datablock = int(fileInode[:4], 16)
    blockList = tfs_get_block_list(datablock)
    blockList.reverse()
    data = LibDisk.readBlock(currentMount, blockList[bAddr])
    data = data[:bOffset * 2] + format("%02X" % ord(byte[0])) +data[(bOffset * 2) + 2:]
    LibDisk.writeBlock(currentMount, blockList[bAddr], data)
    ResourceTable[FD][1] += 1


if __name__ == '__main__':
    fs = tfs_mkfs(DEFAULT_DISK_NAME, 270)
    df = tfs_mount(DEFAULT_DISK_NAME)
    one = tfs_open("test.txt")
    print(one)
    tfs_open("7chars")
    #tfs_close(2)
    str1 = "HELLO THERE GENERAL KENOBI YOU ARE A BOLD ONE"
    tfs_write(one, str1)
    for i in range(len(str1)):
        print(tfs_readByte(one))
    tfs_close(one)
    one = tfs_open("test.txt")
    tfs_makeRO(one)
    str2 = "different string"
    tfs_write(one, str2)
    tfs_delete(one)
    tfs_makeRW(one)
    tfs_write(one, str2)
    for i in range(len(str2)):
        if i == 2:
            tfs_writeByte(one, "B")
        print(tfs_readByte(one))
    print(ResourceTable)
    tfs_delete(one)
    print(ResourceTable)
    tfs_unmount(df)
