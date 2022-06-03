import TinyFS 
from TinyFS import *

"""tfs_mkfs
tfs_mount
tfs_unmount
tfs_open
tfs_close
tfs_write
tfs_delete
tfs_readByte
tfs_seek
tfs_makeRO
tfs_makeRW
tfs_writeByte
tfs_readdir
tfs_rename"""

if __name__ == '__main__':

    disk_store = tfs_mkfs(DEFAULT_DISK_NAME, DEFAULT_DISK_SIZE)
    file_system = tfs_mount(DEFAULT_DISK_NAME)
    first_file = tfs_open("frst.txt")
    input_string = "filler data for first file"
    print("This is our SuperBlock at initialization")
    print(LibDisk.readBlock(file_system, 0))

    print("\nUpon opening a file it is added to the resource table shown below in the format {FD: [file name, index into file, file inode block address, Read only boolean]}")
    print(ResourceTable)
    print("The '3' in the resource table represents the index 3 block, which will contain that file's inode, which we use to find the first data block for the file \n")
    
    print("The contents of that file before being written to look like this, with the hexadecimal values towards the begining storig the name of the file")
    print(LibDisk.readBlock(file_system, 4))
    print("Next if we write to this file we will add data, in this case we will add the text \"filler data for first file\" which will make the data block look like")
    tfs_write(first_file, input_string)

    print(LibDisk.readBlock(file_system, 4))

    print("we can then use tfs_readbyte to read the file which results in")

    for i in range(len(input_string)):
        print(tfs_readByte(first_file), end = "")
    print("\n")

    print("we can combine this with seek to print the byte at a certain point, here we will print the tenth byte in the file")
    tfs_seek(first_file, 0)
    print(tfs_readByte(first_file))
    tfs_close(first_file)



    


    

