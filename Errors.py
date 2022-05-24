class nBytesError(Exception):
    def __init__(self, nbytes):
        self.message = nbytes + " is not a multiple of 256"
        super().__init__(self.message)