WORD_SIZE = 2 # bytes

class CacheBlock(object):
    def __init__(self, block_size=64):
        self.words = ['' for x in xrange(block_size/WORD_SIZE)]
        self.state = 'I' # MESI
        self.block_size = block_size
    
    def insert_word(self, address):
        '''
            Takes an address,
            finds the offset in the block to insert the address.
            Also, fills up the whole block with the neighbouring addresses.
            E.g. if we have the following config: block size 8, word size 2,
            we will have 4 words in 1 block.
            If we have the address 6, after inserting the address,
            the block will look like:
            [0, 2, 4, 6]
        '''
        block_offset = self._map_address_to_block_offset(address)
        self.words[block_offset] = address
        for x in xrange(block_offset+1, len(self.words)):
            self.words[x] = address+WORD_SIZE
        for x in xrange(block_offset-1, -1, -1):
            self.words[x] = address-WORD_SIZE
        
    def _map_address_to_block_offset(self, address):
        return address % self.block_size
