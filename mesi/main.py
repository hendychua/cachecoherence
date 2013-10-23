import argparse
from processor import Processor, FETCH_INSTRUCTION, \
                        READ_MEMORY, WRITE_MEMORY

def main(config):
    processors = []
    all_instructions = []
    for i in xrange(config.num_processors):
        proc = Processor(config.associativity, config.block_size, config.cache_size)
        processors.append(proc)

    path = ""
    prefix = ""
    if config.input_file == "FFT":
        path = "../fft/fft%s/"%config.num_processors
        prefix = "FFT"
    elif config.input_file == "WEATHER":
        path = "../weather/weather%s/"%config.num_processors
        prefix = "WEATHER"

    for i in xrange(1, config.num_processors+1):
        print "loading instructions for proc %s"%i
        inst = []
        with open(path+prefix+str(i)+".prg", "r") as f:
            for l in f:
                inst.append(l.strip("\n"))
        all_instructions.append(inst)
    
    print "finish loading instructions for %s processors"%config.num_processors
    
    total_i = 0
    for i in all_instructions:
        total_i += len(i)
    i_executed = 0
    print "total_i: %s"%total_i
    while still_got_instructions(all_instructions): 
        # print "i_executed: %s"%i_executed
        for i,proc in enumerate(processors):
            curr_inst = all_instructions[i][0] if all_instructions[i] else None
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
                elif instruction_type == FETCH_INSTRUCTION:
                    ret = proc.execute(curr_inst) 
                if ret == proc.NOT_STALLED:
                    all_instructions[i].pop(0)
                    # i_executed += 1
                elif ret == proc.STALLED:
                    pass
    
    with open('result_%s%s'%(prefix, config.num_processors), 'w+') as f:
        for i, p in enumerate(processors):
            f.write("*********************")
            f.write("processor %s results:"%i)
            f.write("total cycles: %s"%p.cycles)
            f.write("total cache accesses: %s"%p.cache.accesses)
            f.write("total cache hits: %s"%p.cache.hits)
            f.write("total cache misses: %s"%p.cache.misses)
            f.write("*********************")

def still_got_instructions(instructions):
    for i in instructions:
        if i:
            return True
    return False
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Description')
    parser.add_argument('protocol', type=str, help='Cache Coherence Protocol', nargs='?', default='MESI', choices=['MESI', 'DRAGON'])
    parser.add_argument('input_file', type=str, help='Input Benchmark Name', nargs='?', default='FFT', choices=['WEATHER', 'FFT'])
    parser.add_argument('num_processors', type=int, help='Number of Processors', nargs='?', default=1)
    parser.add_argument('cache_size', type=int, help='Cache Size in Bytes', nargs='?', default=4096)
    parser.add_argument('associativity', type=int, help='Associativity of the cache', nargs='?', default=1)
    parser.add_argument('block_size', type=int, help='Block Size in Bytes', nargs='?', default=64)
    main(parser.parse_args())