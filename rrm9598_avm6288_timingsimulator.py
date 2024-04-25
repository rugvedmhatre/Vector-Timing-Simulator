# -------------------------------------------------------------
# Title   : Vector Processor - Timing Simulator
# Authors : Rugved Mhatre (rrm9598), Akshath Mahajan (avm6288)
# -------------------------------------------------------------

import os
import argparse

class Config(object):
    def __init__(self, iodir):
        self.filepath = os.path.abspath(os.path.join(iodir, "Config.txt"))
        self.parameters = {} # dictionary of parameter name: value as strings.

        try:
            with open(self.filepath, 'r') as conf:
                self.parameters = {line.split('=')[0].strip(): line.split('=')[1].split('#')[0].strip() for line in conf.readlines() if not (line.startswith('#') or line.strip() == '')}
            
            for key in self.parameters.keys():
                # Converting config values from string to int
                self.parameters[key] = int(self.parameters[key])
            
            print("Config - Parameters loaded from file:", self.filepath)
            # print("Config parameters:", self.parameters)
        except:
            print("Config - ERROR: Couldn't open file in path:", self.filepath)
            raise

class IMEM(object):
    def __init__(self, iodir):
        self.size = pow(2, 16) # Can hold a maximum of 2^16 instructions.
        self.filepath = os.path.abspath(os.path.join(iodir, "Resolved_Code.txt"))
        self.instructions = []

        try:
            with open(self.filepath, 'r') as insf:
                self.instructions = [ins.split('#')[0].strip() for ins in insf.readlines() if not (ins.startswith('#') or ins.strip() == '')]
            print("IMEM - Instructions loaded from file:", self.filepath)
            # print("IMEM - Instructions:", self.instructions)
        except:
            print("IMEM - ERROR: Couldn't open file in path:", self.filepath)
            raise

    def Read(self, idx): # Use this to read from IMEM.
        if idx < self.size:
            return self.instructions[idx]
        else:
            print("IMEM - ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)

class DMEM(object):
    # Word addressible - each address contains 32 bits.
    def __init__(self, name, iodir, addressLen):
        self.name = name
        self.size = pow(2, addressLen)
        self.min_value  = -pow(2, 31)
        self.max_value  = pow(2, 31) - 1
        self.ipfilepath = os.path.abspath(os.path.join(iodir, name + ".txt"))
        self.opfilepath = os.path.abspath(os.path.join(iodir, name + "OP.txt"))
        self.data = []

        try:
            with open(self.ipfilepath, 'r') as ipf:
                self.data = [int(line.strip()) for line in ipf.readlines()]
            print(self.name, "- Data loaded from file:", self.ipfilepath)
            # print(self.name, "- Data:", self.data)
            self.data.extend([0x0 for i in range(self.size - len(self.data))])
        except:
            print(self.name, "- ERROR: Couldn't open input file in path:", self.ipfilepath)
            raise

    def Read(self, idx): # Use this to read from DMEM.
        pass # Replace this line with your code here.

    def Write(self, idx, val): # Use this to write into DMEM.
        pass # Replace this line with your code here.

    def dump(self):
        try:
            with open(self.opfilepath, 'w') as opf:
                lines = [str(data) + '\n' for data in self.data]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", self.opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", self.opfilepath)
            raise

class RegisterFile(object):
    def __init__(self, name, count, length = 1, size = 32):
        self.name       = name
        self.reg_count  = count
        self.vec_length = length # Number of 32 bit words in a register.
        self.reg_bits   = size
        self.min_value  = -pow(2, self.reg_bits-1)
        self.max_value  = pow(2, self.reg_bits-1) - 1
        self.registers  = [[0x0 for e in range(self.vec_length)] for r in range(self.reg_count)] # list of lists of integers

    def Read(self, idx):
        pass # Replace this line with your code.

    def Write(self, idx, val):
        pass # Replace this line with your code.

    def dump(self, iodir):
        opfilepath = os.path.abspath(os.path.join(iodir, self.name + ".txt"))
        try:
            with open(opfilepath, 'w') as opf:
                row_format = "{:<13}"*self.vec_length
                lines = [row_format.format(*[str(i) for i in range(self.vec_length)]) + "\n", '-'*(self.vec_length*13) + "\n"]
                lines += [row_format.format(*[str(val) for val in data]) + "\n" for data in self.registers]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", opfilepath)
            raise

class Queue():
    def __init__(self, max_length: int):
        self.queue = []
        self.max_length = max_length
    
    def add(self, item):
        if (len(self.queue) < self.max_length):
            self.queue.append(item)
            return True
        else:
            print("ERROR - Queue already full!")
            return False
        
    def pop(self):
        if (len(self.queue) > 0):
            item = self.queue[0]
            self.queue = self.queue[1:]
            return item
        else:
            print("ERROR - Queue is empty!")
            return None
        
    def __str__(self):
        return_string = '[' + ", ".join(self.queue) + ']'
        return return_string

class Core():
    def __init__(self, imem: IMEM, sdmem: DMEM, vdmem: DMEM, config: Config):
        # cycle counter
        self.cycle = 0

        self.RFs = {"SRF": RegisterFile("SRF", 8),
                    "VRF": RegisterFile("VRF", 8, 64)}
        
        
    def run(self):
        # Printing current VMIPS configuration
        print("")
        print("VMIPS Configuration :")
        for key in config.parameters.keys():
            if len(key) < 15:
                print(key, "\t\t:" , config.parameters[key])
            else:
                print(key, "\t:" , config.parameters[key])
        print("")

        # Line Number to iterate through the code file
        line_number = 0

        while(True):
            # --- FETCH Stage ---
            current_instruction = imem.Read(line_number)
            current_instruction = current_instruction.split(" ")

            print("Current Instruction :", current_instruction)
            print("")

            # --- DECODE + EXECUTE + WRITEBACK Stage ---
            instruction_word = current_instruction[0]
            # print("Instruction Word    : ", instruction_word)

            if instruction_word == "HALT":
                # --- EXECUTE : HALT --- 
                self.cycle += 1
                break

            line_number += 1
            self.cycle += 1
        
        print("------------------------------")
        print(" Total Cycles: ", self.cycle)
        print("------------------------------")

    def dumpregs(self, iodir):
        for rf in self.RFs.values():
            rf.dump(iodir)

if __name__ == "__main__":
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Functional Simulator')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
    args = parser.parse_args()

    iodir = os.path.abspath(args.iodir)
    print("IO Directory:", iodir)

    # Parse Config
    config = Config(iodir)

    # Parse IMEM
    imem = IMEM(iodir)  
    # Parse SMEM
    sdmem = DMEM("SDMEM", iodir, 13) # 32 KB is 2^15 bytes = 2^13 K 32-bit words.
    # Parse VMEM
    vdmem = DMEM("VDMEM", iodir, 17) # 512 KB is 2^19 bytes = 2^17 K 32-bit words. 

    # Create Vector Core
    vcore = Core(imem, sdmem, vdmem, config)

    # Run Core
    vcore.run()   
    # vcore.dumpregs(iodir)

    # sdmem.dump()
    # vdmem.dump()

    # THE END