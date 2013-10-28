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
        log.info("instruction_file: %s"%instruction_file)
        instructions.append(Instruction(instruction_file))
        proc = Processor(i, config.protocol, config.associativity, config.block_size, config.cache_size)
        processors.append(proc)
    log.info("Finished loading processors and instructions.")
    
    running_processors = config.num_processors
    start_time = datetime.utcnow()
    while running_processors > 0:
        running_processors = 0
        for i,processor in enumerate(processors):
            if processor.stall_status == processor.NOT_STALLED:
                if instructions[i].ended is False:
                    instruction = instructions[i].next()
                    if instruction:
                        bus_transaction, address = processor.check_for_bus_transaction_needed(instruction)
                        if bus_transaction == processor.NO_BUS:
                            # no need to do send bus transactions
                            processor.execute(instruction)
                        elif bus_transaction == processor.BUS_READ:
                            snoop_reports = []
                            for x,p in enumerate(processors):
                                if x!=i:
                                    snoop_reports.append(p.snoop(bus_transaction, address))
                            if processor.INTERESTED in snoop_reports:
                                processor.execute(instruction, read_type='S')
                            else:
                                # no one is interested, we read as exclusive
                                processor.execute(instruction, read_type='E')
                        
                        elif bus_transaction == processor.BUS_READ_EXCLUSIVE:
                            snoop_reports = []
                            for x,p in enumerate(processors):
                                if x!=i:
                                    snoop_reports.append(p.snoop(bus_transaction, address))
                            # for BUS_READ_EXCLUSIVE, we just want to invalidate other copies
                            # hence no need to check if anyone is interested
                            processor.execute(instruction)
                        
                        running_processors += 1
            
            elif processor.stall_status == processor.STALLED:
                # pass in empty as we just want the cycle to go through and the processor to reduce its latency
                processor.execute("")
                running_processors += 1
                        
    end_time = datetime.utcnow()
    for i, processor in enumerate(processors):
        log.info("***")
        log.info("p%s total cycles needed: %s"%(processor.identifier, processor.cycles))
        log.info("total instructions: %s"%(instructions[i].count))
        log.info("fetch instructions: %s"%(processor.fetch_instructions))
        log.info("bus read transactions sent: %s"%processor.bus_transactions_count[0])
        log.info("bus read exclusive transactions sent: %s"%processor.bus_transactions_count[1])
        log.info("cache hits: %s cache misses: %s"%(processor.cache.hits, processor.cache.misses))
        log.info("hit ratio: %s miss ratio: %s"%(float(processor.cache.hits)/processor.cache.accesses, float(processor.cache.misses)/processor.cache.accesses))
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