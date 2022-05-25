class nBytesError(Exception):
    def __init__(self, nbytes):
        self.message = str(nbytes) + " is not a positive multiple of 256"
        self.exit_num = -1
        super().__init__(self.message)

class diskNotFound(FileNotFoundError):
    def __init__(self, filename):
        self.message = filename + " is not a recognized disk" 
        self.exitnumber = -2
        super().__init__(self.message)


