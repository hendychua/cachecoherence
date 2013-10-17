from processor import Processor, FETCH_INSTRUCTION, \
                        READ_MEMORY, WRITE_MEMORY

def main():
    num_processors = 4
    block_size = 64
    cache_size = 4096
    processors = []
    all_instructions = []
    for i in xrange(num_processors):
        proc = Processor(block_size, cache_size)
        processors.append(proc)
        # TODO: for each processor, read the trace file for it
        #       and load the instructions into an array inst.
        #       Each element in the array inst is 1 instruction
        #       i.e. 1 line read from the trace file
        inst = []
        all_instructions.append(inst)
    
    while still_got_instructions(all_instructions):
        for i,proc in enumerate(processors):
            curr_inst = instructions[i][0] if instructions[i] else None
            if curr_inst:
                instruction_type, address = curr_inst.split()
                instruction_type = int(instruction_type)
                ret = None
                if instruction_type == READ_MEMORY:
                    snoop_reports = [p.snoop('BUSREAD', address) for x,p in enumerate(processors) if x!=i]
                    if proc.INTERESTED in snoop_reports:
                        ret = proc.execute(curr_inst, read_type='S')
                    else:
                        # no one else is interested. can read as exclusive
                        ret = proc.execute(curr_inst, read_type='E')
                elif instruction_type == WRITE_MEMORY:
                    # for BUSREAD_X, we just snoop to tell others to invalidate their copy,
                    # so we don't really have to check the snoop reports for anything
                    snoop_reports = [p.snoop('BUSREAD_X', address) for x,p in enumerate(processors) if x!=i]
                    ret = proc.execute(curr_inst)
                if ret == proc.NOT_STALLED:
                    instructions[i] = instructions[i][1:] #remove the instruction that has just been processed
                elif ret == proc.STALLED:
                    pass

def still_got_instructions(instructions):
    for i in instructions:
        if i:
            return True
    return False
    
if __name__ == "__main__":
    main()