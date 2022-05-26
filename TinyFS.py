# Makes an empty TinyFS file system of size nBytes on the file specified by ‘filename’. 
#This function should use the emulated disk library to open the specified file, and upon success, format the file to be mountable. 
#This includes initializing all data to 0x00, setting magic numbers, initializing and writing the superblock and other metadata, etc. 
#Must return a specified success/error code. */
def tfs_mkfs(char *filename, int nBytes):

#/* tfs_mount(char *filename) “mounts” a TinyFS file system located within ‘filename’.
# tfs_unmount(void) “unmounts” the currently mounted file system. As part of the mount operation, tfs_mount should verify the file system is the correct type.#
# Only one file system may be mounted at a time. Use tfs_unmount to cleanly unmount the currently mounted file system.
# Must return a specified success/error code. */
def tfs_mount(char *filename):
def tfs_unmount(void):

#/* Opens a file for reading and writing on the currently mounted file system.#
# Creates a dynamic resource table entry for the file (the structure that tracks open files, the internal file pointer, etc.),
# and returns a file descriptor (integer) that can be used to reference this file while the filesystem is mounted. */
def tfs_open(char *name):

#/* Closes the file and removes dynamic resource table entry */
def tfs_close(fileDescriptor FD):

#/* Writes buffer ‘buffer’ of size ‘size’, which represents an entire file’s contents, to the file described by ‘FD’.#
# Sets the file pointer to 0 (the start of file) when done. Returns success/error codes. */
def tfs_write(fileDescriptor FD, char *buffer, int size):

#/* deletes a file and marks its blocks as free on disk. */
def tfs_delete(fileDescriptor FD):

#/* reads one byte from the file and copies it to ‘buffer’, using the current file pointer location and incrementing it by one upon success.
# If the file pointer is already at the end of the file then tfs_readByte() should return an error and not increment the file pointer. */
def tfs_readByte(fileDescriptor FD, char *buffer):

#/* change the file pointer location to offset (absolute). Returns success/error codes.*/
def tfs_seek(fileDescriptor FD, int offset):

#You must also include the following definitions someplace within the library (given in C):

#/* The default size of the disk and file system block */
define BLOCKSIZE 256

#/* Your program should use a 10240 byte disk size giving you 40 blocks total. This is the default size. You must be able to support different possible values, or report an error if it exceeds the limits of your implementation. */
define DEFAULT_DISK_SIZE 10240 

#/* use this name for a default disk file name */
#define DEFAULT_DISK_NAME “tinyFSDisk” 	
typedef int fileDescriptor: