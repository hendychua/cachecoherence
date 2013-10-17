import math
from cacheblock import CacheBlock

class Cache(object):
    CACHE_HIT = 1
    CACHE_MISS = 0
    
    def __init__(self, block_size=64, cache_size=4096):
        '''
            Assumption(s): all direct-mapped cache
        '''
        self.sets = [None for x in xrange(cache_size/block_size)]
        self.accesses = 0 # every read or write access regardless of hits/miss will increment this counter
        self.hits = 0
        self.misses = 0 #hits + misses = accesses
        self.block_size = block_size
    
    def read(self, address, read_type='S'):
        # caller of this method should check return type.
        # if its a CACHE_MISS, caller is responsible for necessary action
        # e.g. stall for 10 cycles.
        self.accesses += 1
        for block in self.sets:
            if address in block.words and block.state in ('M', 'E', 'S'):
                self.hits += 1
                return self.CACHE_HIT
        else:
            # it is a miss if the block is not found or the state is I.
            self.misses += 1
            newblock = CacheBlock(self.block_size)
            newblock.insert_word(address)
            newblock.state = read_type # E or S
            self._insert_block(newblock)
            return self.CACHE_MISS

    def write(self, address):
        self.accesses += 1
        for block in self.sets:
            if address in block.words and block.state in ('M', 'E', 'S'):
                block.state = 'M'
                self.hits += 1
                return CACHE_HIT
        else:
            # caller of this method should check return type.
            # if its a CACHE_MISS, caller is responsible for necessary action
            # e.g. stall for 10 cycles.
            self.misses += 1
            newblock = CacheBlock(self.block_size)
            newblock.insert_word(address)
            newblock.state = 'M'
            self._insert_block(newblock)
            return CACHE_MISS

    def _insert_block(self, cache_block):
        # first word of the cache_block must be filled with the address
        # cos that is the address I use to get the set index
        index = self._map_address_to_set_index(cache_block.words[0])
        self.cache_sets[index] = cache_block
        
    def _map_address_to_set_index(self, address):
        block_number = math.floor(int(address, 16)/self.block_size)        
        return block_number % len(self.sets)