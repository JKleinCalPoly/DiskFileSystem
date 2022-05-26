from os.path import exists
from Errors import *

BLOCKSIZE = 10

class diskFile:
    def __init__(self, fd, nBytes):
        self.fd = fd
        self.nBytes = nBytes

# This function opens a regular UNIX file and designates the first nBytes of it as space for the emulated disk.
# nBytes should be a number that is evenly divisible by the block size.
# If nBytes > 0 and there is already a file by the given filename, that disk is resized to nBytes,
# and that file’s contents may be overwritten. If nBytes is 0, an existing disk is opened,
# and should not be overwritten. There is no requirement to maintain integrity of any content beyond nBytes.
# Errors must be returned for any other failures, as defined by your own error code system.''

# return file descriptor of current open disk
def openDisk(filename, nBytes):
    try:
        if nBytes == 0:
            if (exists(filename)):
                disk = open (filename, 'w')
                #TODO: how to find nbytes of previously created disk
            else:
                raise diskNotFound (filename)
        elif (nBytes < 0):
            raise nBytesError (nBytes)
        else:
            if nBytes % BLOCKSIZE == 0:
                disk = open (filename, 'w+')
            else:
                raise nBytesError(nBytes)
    except Exception as e:
        print(e.message)
        exit(e.exit_num)

    return diskFile(disk, nBytes)

# readBlock() reads an entire block of BLOCKSIZE bytes from the open disk (identified by ‘disk’) and
# copies the result into a local buffer (must be at least of BLOCKSIZE bytes).
# The bNum is a logical block number, which must be translated into a byte offset within the disk.
# The translation from logical to physical block is straightforward: bNum=0 is the very first byte of the file.
# bNum=1 is BLOCKSIZE bytes into the disk, bNum=n is n*BLOCKSIZE bytes into the disk. On success, it returns the value of the block.
# Errors must be returned if ‘disk’ is not available (i.e. hasn’t been opened) or for any other failures,
# as defined by your own error code system.

def readBlock(disk, bNum):
    try:
        if bNum >= disk.nBytes:
            raise readOOBError(bNum)
        disk.fd.seek(bNum * BLOCKSIZE)
        block = disk.fd.read(BLOCKSIZE)
        #TODO: python will read to EOF if BLOCKSIZE > chars in file, is this a problem?
    except FileNotFoundError as e:
        print(e)
        exit(-1)
    except readOOBError as e:
        print(e)
        exit(e.exitnumber)
    return block

# writeBlock() takes disk number ‘disk’ and logical block number ‘bNum’ and writes the content of the buffer
# ‘block’ to that location. BLOCKSIZE bytes will be written from ‘block’ regardless of its actual size.
# The disk must be open. Just as in readBlock(), writeBlock() must translate the logical block
# bNum to the correct byte position in the file. On success, it returns 0.
# Errors must be returned if ‘disk’ is not available (i.e. hasn’t been opened) or for any other failures,
# as defined by your own error code system.
def writeBlock(disk, bNum, block):
    try:
        if bNum >= disk.nBytes:
            raise writeOOBError(bNum)
        disk.fd.seek(bNum * BLOCKSIZE)
        for i in range(BLOCKSIZE):
            if i >= len(block):
                disk.fd.write('0')
            else:
                disk.fd.write(block[i])
    except FileNotFoundError as e:
        print(e)
        exit(-1)
    except writeOOBError as e:
        print(e)
        exit(e.exitnumber)
    return 0

# closeDisk() takes a disk number ‘disk’ and makes the disk closed to further I/O;
# i.e. any subsequent reads or writes to a closed disk should return an error.
# Closing a disk should also close the underlying file, committing any writes being buffered by the real OS.
def closeDisk(disk):
    try:
        disk.fd.close()
    except Exception as e:
        print(e.message)
        exit(e.exit_num)

if __name__ == '__main__':
    disk1 = openDisk("libDiskFile.img", BLOCKSIZE * 5)
    #disk1 = openDisk("libDiskFile.img", 0)
    writeBlock(disk1, 1, '5' * 6)
    writeBlock(disk1, 3, 'b' * 3)
    print(readBlock(disk1, 1))
    closeDisk(disk1)

# Makes an empty TinyFS file system of size nBytes on the file specified by ‘filename’. 
#This function should use the emulated disk library to open the specified file, and upon success, format the file to be mountable. 
#This includes initializing all data to 0x00, setting magic numbers, initializing and writing the superblock and other metadata, etc. 
#Must return a specified success/error code. */
int tfs_mkfs(char *filename, int nBytes);

#/* tfs_mount(char *filename) “mounts” a TinyFS file system located within ‘filename’.
# tfs_unmount(void) “unmounts” the currently mounted file system. As part of the mount operation, tfs_mount should verify the file system is the correct type.#
# Only one file system may be mounted at a time. Use tfs_unmount to cleanly unmount the currently mounted file system.
# Must return a specified success/error code. */
int tfs_mount(char *filename);
int tfs_unmount(void);

#/* Opens a file for reading and writing on the currently mounted file system.#
# Creates a dynamic resource table entry for the file (the structure that tracks open files, the internal file pointer, etc.),
# and returns a file descriptor (integer) that can be used to reference this file while the filesystem is mounted. */
fileDescriptor tfs_open(char *name);

#/* Closes the file and removes dynamic resource table entry */
int tfs_close(fileDescriptor FD);

#/* Writes buffer ‘buffer’ of size ‘size’, which represents an entire file’s contents, to the file described by ‘FD’.#
# Sets the file pointer to 0 (the start of file) when done. Returns success/error codes. */
int tfs_write(fileDescriptor FD, char *buffer, int size);

#/* deletes a file and marks its blocks as free on disk. */
int tfs_delete(fileDescriptor FD);

#/* reads one byte from the file and copies it to ‘buffer’, using the current file pointer location and incrementing it by one upon success.
# If the file pointer is already at the end of the file then tfs_readByte() should return an error and not increment the file pointer. */
int tfs_readByte(fileDescriptor FD, char *buffer);

#/* change the file pointer location to offset (absolute). Returns success/error codes.*/
int tfs_seek(fileDescriptor FD, int offset);

#You must also include the following definitions someplace within the library (given in C):

#/* The default size of the disk and file system block */
define BLOCKSIZE 256

#/* Your program should use a 10240 byte disk size giving you 40 blocks total. This is the default size. You must be able to support different possible values, or report an error if it exceeds the limits of your implementation. */
define DEFAULT_DISK_SIZE 10240 

#/* use this name for a default disk file name */
#define DEFAULT_DISK_NAME “tinyFSDisk” 	
typedef int fileDescriptor;
