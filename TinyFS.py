import LibDisk
from LibDisk import *
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"

ResourceTable = {} #format {FD: [name, inode addr, index]}
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
            print(name + " not found")
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
                rootdirectory = rootdirectory[:sliceStart] + entry + rootdirectory[sliceEnd:]
                bitmap = superblock[10:]
                nextInode, bitmap = tfs_alloc(bitmap)
                nextData, bitmap = tfs_alloc(bitmap)
                superblock = superblock[:10] + bitmap
                newInode = hex(nextData)[2:]
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
    superblock = superblock[0:6] + fileinode + superblock[10:]
    print(superblock)
    LibDisk.writeBlock(currentMount, 0, superblock)
    LibDisk.writeBlock(currentMount, 2, rootdirectory)
    fd = fdIndex
    fdIndex += 1
    ResourceTable.update({fd:[name, 0, fileinode]})
    return fd

def tfs_alloc(bitmap):
    for i, c in enumerate(bitmap):
        if c != 'F':
            binr = bin(int(c, 16))[2:].zfill(4)
            print(binr)
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
def tfs_write(FD, buffer, size):
    return 0
#/* deletes a file and marks its blocks as free on disk. */
def tfs_delete(FD):
    return 0
#/* reads one byte from the file and copies it to ‘buffer’, using the current file pointer location and incrementing it by one upon success.
# If the file pointer is already at the end of the file then tfs_readByte() should return an error and not increment the file pointer. */
def tfs_readByte(FD, buffer):
    byte = 0
    return byte

#/* change the file pointer location to offset (absolute). Returns success/error codes.*/
def tfs_seek(FD, offset):
    return 0

if __name__ == '__main__':
    fs = tfs_mkfs(DEFAULT_DISK_NAME, 180)
    df = tfs_mount(DEFAULT_DISK_NAME)
    tfs_open("test.txt")
    tfs_open("7chars")
    tfs_close(2)
    print(ResourceTable)
    tfs_unmount(df)
