import math
from cacheblock import CacheBlock

MES = ('M', 'E', 'S')

class Cache(object):
    CACHE_HIT_SHARED = 3
    CACHE_HIT_MODIFIED = 2
    CACHE_HIT_EXCLUSIVE = 1
    CACHE_MISS = 0
    
    def __init__(self, associativity=1, block_size=64, cache_size=4096):
        self.associativity = associativity
        self.sets = [[None for x in xrange(associativity)] for y in xrange((cache_size/block_size)/associativity)]
        self.accesses = 0 # every read or write access regardless of hits/miss will increment this counter
        self.hits = 0
        self.misses = 0 #hits + misses = accesses
        self.block_size = block_size
    
    def is_address_present(self, address, update_hits_misses_count=False):
        if update_hits_misses_count:
            self.accesses += 1
        set_index = int((math.floor(address/self.block_size)) % len(self.sets))
        blockset = self.sets[set_index]
        for block in blockset:
            if block is not None and address in block.words and block.state in MES:
                if update_hits_misses_count:
                    self.hits += 1
                if block.state == "M":
                    return self.CACHE_HIT_MODIFIED
                elif block.state == "E":
                    return self.CACHE_HIT_EXCLUSIVE
                elif block.state == "S":
                    return self.CACHE_HIT_SHARED
        else:
            # it is a miss if the block is not found or the state is I.
            if update_hits_misses_count:
                self.misses += 1
            return self.CACHE_MISS
    
    def read(self, address, read_type="S"):
        newblock = CacheBlock(self.block_size)
        newblock.insert_word(address)
        newblock.state = read_type # E or S
        self._insert_block(newblock)

    def write(self, address):
        newblock = CacheBlock(self.block_size)
        newblock.insert_word(address)
        newblock.state = 'M'
        self._insert_block(newblock)

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
        