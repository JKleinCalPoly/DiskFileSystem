import LibDisk
from LibDisk import *
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"

ResourceTable = {} #format {FD: (name, progress/index)}
global currentMount
currentMount = None

# Makes an empty TinyFS file system of size nBytes on the file specified by ‘filename’.
#This function should use the emulated disk library to open the specified file, and upon success, format the file to be mountable. 
#This includes initializing all data to 0x00, setting magic numbers, initializing and writing the superblock and other metadata, etc. 
#Must return a specified success/error code. */
def tfs_mkfs(filename, nBytes):
    disk = LibDisk.openDisk(filename, nBytes)
    for i in range(int(nBytes / LibDisk.BLOCKSIZE)):
        if i == 0:
            LibDisk.writeBlock(disk, i, "5A00010001")
        elif i == 1:
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
        print(FD.nBytes)
        currentMount = FD
    except Exception as e:
        print(e)
        exit(-1)

    block = LibDisk.readBlock(FD, 0)
    if not block.startswith("5A"):
        print(block)
        raise DiskFormatError(filename)
    return FD

def tfs_unmount(diskFile):
    LibDisk.closeDisk(diskFile)
    return 0

#/* Opens a file for reading and writing on the currently mounted file system.#
# Creates a dynamic resource table entry for the file (the structure that tracks open files, the internal file pointer, etc.),
# and returns a file descriptor (integer) that can be used to reference this file while the filesystem is mounted. */
def tfs_open(name):
    ResourceTable.update({fd:(name, 0)})
    return fd

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
    #fs = tfs_mkfs(DEFAULT_DISK_NAME, 90)
    df = tfs_mount(DEFAULT_DISK_NAME)
    print(df)