class nBytesError(Exception):
    def __init__(self, nbytes):
        self.message = nbytes + " is not a multiple of 256"
        super().__init__(self.message)

class diskNotFound(FileNotFoundException):
    def __init__(self, filename):
        self.message = filename + " is not a recognized disk" 
        self.exitnumber = -2
        super().__init__(self.message)
