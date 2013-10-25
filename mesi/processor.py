import math
import logging
from cache import Cache

FETCH_INSTRUCTION = 0
READ_MEMORY = 2
WRITE_MEMORY = 3

MES = ('M', 'E', 'S')

class Processor(object):
    INTERESTED = 1
    NOT_INTERESTED = 0
    NOT_STALLED = 0
    STALLED = 1
    
    def __init__(self, identifier, protocol="MESI", associativity=1, block_size=64, cache_size=4096):
        self.cache = Cache(associativity=associativity, block_size=block_size, cache_size=cache_size)
        self.cycles = 0
        self.latency = 0
        self.fetch_instructions = 0
        self.identifier = identifier
        self.protocol = protocol
        self.log = logging.getLogger("p"+str(identifier))

    def execute(self, instruction, read_type='S'):
        # when the execute function is called, it will check if there are
        # any latencies. if self.latency != 0, self.latency will decrease by
        # 1 cycle and instruction won't be executed. If self.latency == 0,
        # the instruction will be executed.
        self.cycles += 1
        instruction_type, address, count = instruction
        if self.latency == 0:
            instruction_type = int(instruction_type)
            if instruction_type == FETCH_INSTRUCTION:
                self.fetch_instructions += 1
            elif instruction_type == READ_MEMORY:
                ret = self.cache.read(address, read_type)
                if ret == self.cache.CACHE_MISS:
                    self.latency = 10
            elif instruction_type == WRITE_MEMORY:
                ret = self.cache.write(address)
                if ret == self.cache.CACHE_MISS:
                    self.latency = 10
            self.log.debug("instruction %s not stalled"%count)
            return self.NOT_STALLED
        else:
            self.log.debug("instruction %s stalled %s"%(count, self.latency))
            self.latency -= 1
            return self.STALLED

    def snoop(self, bus_transaction_type, address):
        if self.protocol == "MESI":
            # TODO: MESI protocol not correct. need to fix
            index = -1
            set_index = int((math.floor(address/self.cache.block_size)) % len(self.cache.sets))
            set_to_search = self.cache.sets[set_index]
            for i, block in enumerate(set_to_search):
                if block is not None and address in block.words and block.state in MES:
                    index = i
                    break
            if index > -1:
                # if block is found in set and state is either M, E or S,
                # we indicate interest
                if bus_transaction_type == "BUSREAD_X":
                    # by right if state is M, we need to flush to memory also.
                    # but the doc says theres a write buffer and assume there are
                    # no latencies for writing to memory, hence don't have to stall.
                    set_to_search[index].state == 'I'
                elif bus_transaction_type == "BUSREAD":
                    set_to_search[index].state == 'S'
                self.log.debug("snoop result: interested in address "+str(address))
                return self.INTERESTED
            else:
                # if block not in sets or state of block is I,
                # just say we are not interested.
                self.log.debug("snoop result: NOT interested in address "+str(address))
                return self.NOT_INTERESTED
        elif self.protocol == "DRAGON":
            # TODO
            pass
        