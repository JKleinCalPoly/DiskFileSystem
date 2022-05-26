from LibDisk import BLOCKSIZE
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"
# Makes an empty TinyFS file system of size nBytes on the file specified by ‘filename’.
#This function should use the emulated disk library to open the specified file, and upon success, format the file to be mountable. 
#This includes initializing all data to 0x00, setting magic numbers, initializing and writing the superblock and other metadata, etc. 
#Must return a specified success/error code. */
def tfs_mkfs(filename, nBytes):
    return 0

#/* tfs_mount(char *filename) “mounts” a TinyFS file system located within ‘filename’.
# tfs_unmount(void) “unmounts” the currently mounted file system. As part of the mount operation, tfs_mount should verify the file system is the correct type.#
# Only one file system may be mounted at a time. Use tfs_unmount to cleanly unmount the currently mounted file system.
# Must return a specified success/error code. */
def tfs_mount(filename):
    disk = 0
    return disk

def tfs_unmount(void):
    return 0

#/* Opens a file for reading and writing on the currently mounted file system.#
# Creates a dynamic resource table entry for the file (the structure that tracks open files, the internal file pointer, etc.),
# and returns a file descriptor (integer) that can be used to reference this file while the filesystem is mounted. */
def tfs_open(name):
    return fd

#/* Closes the file and removes dynamic resource table entry */
def tfs_close(FD):
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