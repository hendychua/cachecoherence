FETCH_INSTRUCTION = 0
READ_MEMORY = 2
WRITE_MEMORY = 3

class Instruction(object):
    def __init__(self, filename):
        self.file = open(filename, 'rb')
        self.ended = False
        self.count = 0
        
    def next(self):
        got_instruction = False
        
        while got_instruction is False:
            line = self.file.readline()
            if line != '':
                self.count += 1
                line = line.rstrip().split(' ')
                instruction_type = int(line[0])
                address = int(line[1], 16)
                if instruction_type == FETCH_INSTRUCTION:
                    # we can just skip fetch instructions since that's not
                    # the focus of this simulation and it has its own instruction cache
                    pass
                else:
                    return (instruction_type, address, self.count)
            else:
                self.file.close()
                self.ended = True
                return None