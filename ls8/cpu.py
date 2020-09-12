"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [00000000] * 256 # memory to hold 256 bytes
        self.reg = [0] * 8          # 8 all purpose registers
        self.pc = 0                 # pc counter
        self.running = True
        self.SP = 7                 # stack pointer
        self.FL = 0b00000000        # flags register, 00000LGE

    def ram_read(self, address):
        # accept the address to read and return the value stored there
        return self.ram[address]

    def ram_write(self, data, address):
        # accept a value to write, and the address to write it to
        self.ram[address] = data

    def load(self):
        """Load a program into memory."""

        address = 0

        # check if 2 arguments are given, if not - exit with error message
        if len(sys.argv) != 2:
            print('To Use: python3 ls8.py examples/filename')
            sys.exit(1)

        # open a file, read in its contents line by line, and save appropriate data into RAM.
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    split_line = line.split("#")
                    cleaned_line = split_line[0].strip()

                    if cleaned_line == '':
                        continue

                    num_to_save = int(cleaned_line, 2)
                    self.ram_write(num_to_save, address)
                    address += 1
        
        except FileNotFoundError:
            print(f'{sys.argv[1]} not found')

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == 0b10100000:                            # ADD R0, R1
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 0b10100010:                          # MUL R0, R1
            product = self.reg[reg_a] * self.reg[reg_b]
            self.reg[reg_a] = product
        elif op == 0b10100111:                          # CMP R0, R1
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001                    # bin 1
            if self.reg[reg_a] < self.reg[reg_b]: 
                self.FL = 0b00000100                    # bin 1 << 2
            if self.reg[reg_a] > self.reg[reg_b]: 
                self.FL = 0b00000010                    # bin 1 << 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def get_arg_count(self, value, comparison=0b11000000):
        x = value & comparison
        x = x >> 6
        return x

    def run(self):
        """Run the CPU."""

        self.reg[self.SP] = 244   # set the stack pointer pointing to hex F4

        while self.running:
            # read the memory address that's stored in register PC, 
                # and store that result in IR, the Instruction Register
            instruction = self.ram[self.pc]

            # Using ram_read(), read the bytes at PC+1 and PC+2 from RAM into 
                # variables operand_a and operand_b in case the instruction needs them.

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # depending on the value of the opcode, perform the actions needed for the 
                # instruction per the LS-8 spec. Maybe an if-elif cascade...?

            if instruction == 0b10000010:         # LDI R0,8
                self.reg[operand_a] = operand_b
                self.pc += self.get_arg_count(instruction) + 1

            elif instruction == 0b01000111:       # PRN R0
                print(self.reg[operand_a])
                self.pc += self.get_arg_count(instruction) + 1

            elif instruction == 0b00000001:       # HLT
                self.running = False

            elif instruction == 0b10100010:       # MUL R0,R1
                self.alu(instruction, operand_a, operand_b)
                self.pc += self.get_arg_count(instruction) + 1

            elif instruction == 0b10100000:       # ADD R0, R1
                self.alu(instruction, operand_a, operand_b)
                self.pc += self.get_arg_count(instruction) + 1

            elif instruction == 0b01000101:       # PUSH
                value_to_save = self.reg[operand_a]
                self.reg[self.SP] -= 1
                self.ram_write(value_to_save, self.reg[self.SP])
                self.pc += self.get_arg_count(instruction) + 1

            elif instruction == 0b01000110:       # POP
                value_to_pop = self.ram_read(self.reg[self.SP])
                self.reg[operand_a] = value_to_pop
                self.reg[self.SP] += 1
                self.pc += self.get_arg_count(instruction) + 1

            elif instruction == 0b01010000:      # CALL
                # operand_a is register
                given_reg = operand_a
                # decrement stack pointer
                self.reg[self.SP] -= 1
                # save return address to stack
                self.ram_write(self.pc + 2, self.reg[self.SP])
                # set the pc to the value of given register
                self.pc = self.reg[given_reg]

            elif instruction == 0b00010001:      # RET
                # set pc to value from top of stack
                self.pc = self.ram[self.reg[self.SP]]
                # pop from stack/move stack pointer
                self.reg[self.SP] += 1

            # Add the CMP instruction and equal flag to your LS-8.
            elif instruction == 0b10100111:                          # CMP R0, R1
                self.alu(instruction, operand_a, operand_b)
                self.pc += self.get_arg_count(instruction) + 1

            # Add the JMP instruction
            elif instruction == 0b01010100:                          # JMP R0
                self.pc = self.reg[operand_a]

            # Add the JEQ and JNE instructions
            elif instruction == 0b01010101:                          # JEQ R0
                if self.FL == '0b1':
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += self.get_arg_count(instruction) + 1

            elif instruction == 0b01010110:                          # JNE R0
                if self.FL != '0b1':
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += self.get_arg_count(instruction) + 1
                
            else:
                print(f'Unknown instruction: {instruction}')
                sys.exit(1)