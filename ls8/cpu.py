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

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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
            else:
                print(f'Unknown instruction: {instruction}')

# first_try = CPU()
# first_try.load()
# first_try.run()