import argparse
import logging
from datetime import datetime
from logging import StreamHandler

from processor import Processor, FETCH_INSTRUCTION, \
                        READ_MEMORY, WRITE_MEMORY
from instruction import Instruction

log = logging.getLogger("main")

def main(config):
    path = ""
    prefix = ""
    if config.input_file == "FFT":
        path = "../fft/fft%s/"%config.num_processors
        prefix = "FFT"
    elif config.input_file == "WEATHER":
        path = "../weather/weather%s/"%config.num_processors
        prefix = "WEATHER"
    
    log.info("Loading processors and instructions.")
    processors = []
    instructions = []
    for i in xrange(config.num_processors):
        instruction_file = path+prefix+str(i+1)+".prg"
        instructions.append(Instruction(instruction_file))
        proc = Processor(i, config.associativity, config.block_size, config.cache_size)
        processors.append(proc)
    log.info("Finished loading processors and instructions.")
    
    running_processors = config.num_processors
    return_statuses = [0, 0, 0, 0]
    start_time = datetime.utcnow()
    while running_processors > 0:
        running_processors = 0
        for i,processor in enumerate(processors):
            if return_statuses[i] == processor.NOT_STALLED:
                if instructions[i].ended is False:
                    instruction = instructions[i].next()
                    if instruction:
                        ret = None 
                        if instruction[0] == READ_MEMORY:
                            snoop_reports = []
                            for x,p in enumerate(processors):
                                if x!=i:
                                    snoop_reports.append(p.snoop('BUSREAD', instruction[1]))
                            if proc.INTERESTED in snoop_reports:
                                ret = proc.execute(instruction, read_type='S')
                            else:
                                # no one else is interested. can read as exclusive
                                ret = proc.execute(instruction, read_type='E')

                        elif instruction[0] == WRITE_MEMORY:
                            # for BUSREAD_X, we just snoop to tell others to invalidate their copy,
                            # so we don't really have to check the snoop reports for anything
                            snoop_reports = []
                            for x,p in enumerate(processors):
                                if x!=i:
                                    snoop_reports.append(p.snoop('BUSREAD', instruction[1]))
                            ret = proc.execute(instruction)

                        elif instruction[0] == FETCH_INSTRUCTION:
                            ret = proc.execute(instruction)
                        return_statuses[i] = ret
                        running_processors += 1
                    
            elif return_statuses[i] == processor.STALLED:
                if instructions[i].ended is False:
                    instruction = instructions[i].curr
                    if instruction:
                        ret = proc.execute(instruction)
                        return_statuses[i] = ret
                        running_processors += 1
    end_time = datetime.utcnow()
    for processor in processors:
        log.info("***")
        log.info("p%s total cycles needed: %s"%(processor.identifier, processor.cycles))
        log.info("cache hits: %s cache misses: %s"%(processor.cache.hits, processor.cache.misses))
        log.info("***")
    log.info("start time %s"%start_time.strftime("%d/%m/%Y %H:%M"))
    log.info("end time %s"%end_time.strftime("%d/%m/%Y %H:%M"))
        
if __name__ == "__main__":
    root = logging.getLogger()

    handler = StreamHandler()
    handler.setFormatter(logging.Formatter("%(name)s: %(msg)s"))

    root.setLevel(logging.INFO)
    root.addHandler(handler)
    
    parser = argparse.ArgumentParser(description='Description')
    parser.add_argument('protocol', type=str, help='Cache Coherence Protocol', nargs='?', default='MESI', choices=['MESI', 'DRAGON'])
    parser.add_argument('input_file', type=str, help='Input Benchmark Name', nargs='?', default='FFT', choices=['WEATHER', 'FFT'])
    parser.add_argument('num_processors', type=int, help='Number of Processors', nargs='?', default=1)
    parser.add_argument('cache_size', type=int, help='Cache Size in Bytes', nargs='?', default=4096)
    parser.add_argument('associativity', type=int, help='Associativity of the cache', nargs='?', default=1)
    parser.add_argument('block_size', type=int, help='Block Size in Bytes', nargs='?', default=64)
    main(parser.parse_args())