class nBytesError(Exception):
    def __init__(self, nbytes):
        self.message = str(nbytes) + " is not a multiple of 256"
        self.exit_num = -1
        super().__init__(self.message)