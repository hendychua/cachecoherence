class Instruction(object):
    def __init__(self, filename):
        self.file = open(filename, 'rb')
        self.ended = False
        self.count = -1
        # self.curr = None
        # self.stalled_readwrite = []
        
    def next(self):
        line = self.file.readline()

        if line != '':
            self.count += 1
            line = line.rstrip().split(' ')
            instruction_type = int(line[0])
            address = int(line[1], 16)
            # self.curr = (instruction_type, address, self.count)
            # return self.curr
            return (instruction_type, address, self.count)
        else:
            self.file.close()
            self.ended = True
            return None