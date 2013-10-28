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
    
    NO_BUS = 0
    BUS_READ = 1
    BUS_READ_EXCLUSIVE = 2
    
    def __init__(self, identifier, protocol="MESI", associativity=1, block_size=64, cache_size=4096):
        self.cache = Cache(associativity=associativity, block_size=block_size, cache_size=cache_size)
        self.cycles = 0
        self.latency = 0
        self.bus_transactions_count = [0, 0] # BUS_READ & BUS_READ_EXCLUSIVE respectively
        self.identifier = identifier
        self.protocol = protocol
        self.log = logging.getLogger("p"+str(identifier))
        self.stall_status = self.NOT_STALLED
    
    def check_for_bus_transaction_needed(self, instruction):
        instruction_type, address, count = instruction
        instruction_type = int(instruction_type)
        # no need since we are not executing fetch instructions
        # if instruction_type == FETCH_INSTRUCTION:
        #     # fetch industrution, no need for bus transactions
        #     return (self.NO_BUS, address)
            
        if instruction_type == READ_MEMORY:
            ret = self.cache.is_address_present(address, update_hits_misses_count=True)
            if ret == self.cache.CACHE_MISS:
                self.bus_transactions_count[0] += 1
                return (self.BUS_READ, address)
            else:
                return (self.NO_BUS, address)
                    
        elif instruction_type == WRITE_MEMORY:
            ret = self.cache.is_address_present(address, update_hits_misses_count=True)
            if ret == self.cache.CACHE_MISS:
                self.bus_transactions_count[1] += 1
                return (self.BUS_READ_EXCLUSIVE, address)
            elif ret == self.cache.CACHE_HIT_MODIFIED:
                return (self.NO_BUS, address)
            elif ret == self.cache.CACHE_HIT_EXCLUSIVE:
                return (self.NO_BUS, address)
            elif ret == self.cache.CACHE_HIT_SHARED:
                self.bus_transactions_count[1] += 1
                return (self.BUS_READ_EXCLUSIVE, address)

    def execute(self, instruction, read_type="S"):
        # when the execute function is called, it will check if there are
        # any latencies. if self.latency != 0, self.latency will decrease by
        # 1 cycle and instruction won't be executed. If self.latency == 0,
        # the instruction will be executed.
        
        self.cycles += 1
        if self.latency > 0:
            self.latency -= 1
            if self.latency == 0:
                self.stall_status = self.NOT_STALLED
            else:
                self.stall_status = self.STALLED
        else:
            instruction_type, address, count = instruction
            instruction_type = int(instruction_type)
            
            # no need since we are not executing fetch instructions
            # if instruction_type == FETCH_INSTRUCTION:
            #     self.stall_status = self.NOT_STALLED

            if instruction_type == READ_MEMORY:
                ret = self.cache.is_address_present(address)
                self.cache.read(address, read_type)
                if ret == self.cache.CACHE_MISS:
                    self.latency = 10
                    self.stall_status = self.STALLED
                else:
                    self.stall_status = self.NOT_STALLED
                    
            elif instruction_type == WRITE_MEMORY:
                ret = self.cache.is_address_present(address)
                self.cache.write(address)
                if ret == self.cache.CACHE_MISS:
                    self.latency = 10
                    self.stall_status = self.STALLED
                else:
                    self.stall_status = self.NOT_STALLED

    def snoop(self, bus_transaction_type, address):
        if self.protocol == "MESI":
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
                if bus_transaction_type == self.BUS_READ_EXCLUSIVE:
                    # by right if state is M, we need to flush to memory also.
                    # but the doc says theres a write buffer and assume there are
                    # no latencies for writing to memory, hence don't have to stall.
                    set_to_search[index].state == 'I'
                elif bus_transaction_type == self.BUS_READ:
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
        