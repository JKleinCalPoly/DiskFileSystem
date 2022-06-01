class nBytesError(Exception):
    def __init__(self, nbytes):
        self.message = str(nbytes) + " is not a positive multiple of 256"
        self.exit_num = -2
        super().__init__(self.message)

class diskNotFound(FileNotFoundError):
    def __init__(self, filename):
        self.message = filename + " is not a recognized disk" 
        self.exitnumber = -3
        super().__init__(self.message)

class writeOOBError(EOFError):
    def __init__(self, nbytes):
        self.message = "Block " + str(nbytes) + " is out of bounds for writing that current disk"
        self.exitnumber = -4
        super().__init__(self.message)

class readOOBError(EOFError):
    def __init__(self, nbytes):
        self.message = "Block " + str(nbytes) + " is out of bounds for that current disk"
        self.exitnumber = -4
        super().__init__(self.message)

class DiskFormatError(Exception):
    def __init__(self, filename):
        self.message = "filename: " + filename + " is not a properly formatted disk"
        self.exitnumber = -5
        super().__init__(self.message)

class TinyFSFileNotFoundError(Exception):
    def __init__(self, fd):
        self.message = "filename: " + fd + " is not and open file on the mounted tinyFS"
        self.exitnumber = -6
        super().__init__(self.message)



