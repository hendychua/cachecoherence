from cache import Cache

FETCH_INSTRUCTION = 0
READ_MEMORY = 2
WRITE_MEMORY = 3

class Processor(object):
    INTERESTED = 1
    NOT_INTERESTED = 0
    NOT_STALLED = 0
    STALLED = 1
    
    def __init__(self, block_size=64, cache_size=4096):
        self.cache = Cache(block_size=block_size, cache_size=cache_size)
        self.cycles = 0
        self.latency = 0
    
    def execute(self, instruction, read_type='S'):
        # when the execute function is called, it will check if there are
        # any latencies. if self.latency != 0, self.latency will decrease by
        # 1 cycle and instruction won't be executed. If self.latency == 0,
        # the instruction will be executed.
        self.cycles += 1
        if self.latency == 0:
            instruction_type, address = instruction.split()
            instruction_type = int(instruction_type)
            if instruction_type == FETCH_INSTRUCTION:
                pass
            if instruction_type in (READ_MEMORY, WRITE_MEMORY):
                if instruction_type == READ_MEMORY:
                    ret = self.cache.read(address, read_type)
                elif instruction_type == WRITE_MEMORY:
                    ret = self.cache.write(address)
                if ret == self.cache.CACHE_MISS:
                    self.latency = 10
            return self.NOT_STALLED
        else:
            self.latency -= 1
            return self.STALLED

    def snoop(self, bus_transaction_type, address):
        index = -1
        for i, block in enumerate(self.cache.sets):
            if address in block.words and block.state in ('M', 'E', 'S'):
                index = i
                break
        if index > -1:
            # if block is found in set and state is either M, E or S,
            # we indicate interest
            if bus_transaction_type == "BUSREAD_X":
                # by right if state is M, we need to flush to memory also.
                # but the doc says theres a write buffer and assume there are
                # no latencies for writing to memory, hence don't have to stall.
                self.cache.sets[index].state == 'I'
            elif bus_transaction_type == "BUSREAD":
                self.cache.sets[index].state == 'S'
            return self.INTERESTED
        else:
            # if block not in sets or state of block is I,
            # just say we are not interested.
            return self.NOT_INTERESTED
        