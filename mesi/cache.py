import math
from cacheblock import CacheBlock

MES = ('M', 'E', 'S')

class Cache(object):
    CACHE_HIT = 1
    CACHE_MISS = 0
    
    def __init__(self, associativity=1, block_size=64, cache_size=4096):
        self.associativity = associativity
        self.sets = [[None for x in xrange(associativity)] for y in xrange((cache_size/block_size)/associativity)]
        self.accesses = 0 # every read or write access regardless of hits/miss will increment this counter
        self.hits = 0
        self.misses = 0 #hits + misses = accesses
        self.block_size = block_size
    
    def read(self, address, read_type='S'):
        # caller of this method should check return type.
        # if its a CACHE_MISS, caller is responsible for necessary action
        # e.g. stall for 10 cycles.
        self.accesses += 1
        set_index = int((math.floor(address/self.block_size)) % len(self.sets))
        blockset = self.sets[set_index]
        for block in blockset:
            if block is not None and address in block.words and block.state in MES:
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
        set_index = int((math.floor(address/self.block_size)) % len(self.sets))
        set_to_search = self.sets[set_index]
        for block in set_to_search:
            if block is not None and address in block.words and block.state in MES:
                block.state = 'M'
                self.hits += 1
                return self.CACHE_HIT
        else:
            # caller of this method should check return type.
            # if its a CACHE_MISS, caller is responsible for necessary action
            # e.g. stall for 10 cycles.
            self.misses += 1
            newblock = CacheBlock(self.block_size)
            newblock.insert_word(address)
            newblock.state = 'M'
            self._insert_block(newblock)
            return self.CACHE_MISS

    def _insert_block(self, cache_block):
        # first word of the cache_block must be filled with the address
        # cos that is the address I use to get the set index
        set_index = int((math.floor(cache_block.words[0]/self.block_size)) % len(self.sets)) #address passed in is in decimal
        set_to_insert = self.sets[set_index]
        i = 0
        for x, block in enumerate(set_to_insert):
            if block is None:
                i = x
                break
        set_to_insert[i] = cache_block
        