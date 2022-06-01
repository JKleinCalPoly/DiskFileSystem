from os.path import exists
from Errors import *

BLOCKSIZE = 30
#TODO: change back to 256 before submit/demo

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
                disk = open (filename, 'r')
                nBytes = int(len(disk.readline()) / (BLOCKSIZE * 2))
                disk.close()
                disk = open(filename, 'r+')
            else:
                raise diskNotFound (filename)
        elif (nBytes < 0):
            raise nBytesError (nBytes)
        else:
            if nBytes % BLOCKSIZE == 0:
                disk = open(filename, 'w+')
            else:
                raise nBytesError(nBytes)
    except Exception as e:
        print(e)
        exit(-1)

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
        disk.fd.seek(bNum * BLOCKSIZE * 2)
        block = disk.fd.read(BLOCKSIZE * 2)
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
    #print(block)
    try:
        if bNum >= disk.nBytes:
            raise writeOOBError(bNum)
        disk.fd.seek(bNum * BLOCKSIZE * 2)
        for i in range(BLOCKSIZE * 2):
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
        print(e)
        exit(-1)

if __name__ == '__main__':
    disk1 = openDisk("libDiskFile.img", BLOCKSIZE * 5)
    closeDisk(disk1)
    disk1 = openDisk("libDiskFile.img", 0)
    writeBlock(disk1, 1, '5' * 6)
    writeBlock(disk1, 1, 'z' * 2)
    writeBlock(disk1, 3, 'b' * 3)
    print(readBlock(disk1, 1))
    closeDisk(disk1)
