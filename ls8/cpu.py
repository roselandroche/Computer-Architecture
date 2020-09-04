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

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 0b10100010:        # MUL R0,R1
            product = self.reg[reg_a] * self.reg[reg_b]
            self.reg[reg_a] = product
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

    def run(self):
        """Run the CPU."""
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

            if instruction == 0b10000010:      # LDI R0,8
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif instruction == 0b01000111:    # PRN R0
                print(self.reg[operand_a])
                self.pc += 2
            elif instruction == 0b00000001:    # HLT
                self.pc += 1
                self.running = False
            elif instruction == 0b10100010:      # MUL R0,R1
                self.alu(instruction, operand_a, operand_b)
                self.pc += 3
            else:
                print(f'Unknown instruction: {instruction}')