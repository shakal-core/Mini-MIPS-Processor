import sys


# ============================================================
# GROUP 4 OPCODES (Integer Values)
# ============================================================

OPCODES = {
    "XOR":  0,   # 0b00000
    "NOR":  1,   # 0b00001
    "ADD":  2,   # 0b00010
    "SUB":  3,   # 0b00011
    "LW":   4,   # 0b00100
    "SW":   5,   # 0b00101
    "ADDI": 6,   # 0b00110
    "SUBI": 7,   # 0b00111
    "AND":  8,   # 0b01000
    "OR":   9,   # 0b01001
    "ANDI": 10,  # 0b01010
    "ORI":  11,  # 0b01011
    "SLL":  12,  # 0b01100
    "SRL":  13,  # 0b01101
    "J":    14,  # 0b01110
    "BEQ":  15,  # 0b01111
    "BNE":  16   # 0b10000
}


R_TYPE = {
    "XOR",
    "NOR",
    "ADD",
    "SUB",
    "AND",
    "OR",
    "SLL",
    "SRL"
}


I_TYPE = {
    "LW",
    "SW",
    "ADDI",
    "SUBI",
    "ANDI",
    "ORI",
    "BEQ",
    "BNE"
}


J_TYPE = {
    "J"
}


# ============================================================
# SEPARATE CONVERSION FUNCTION
# ============================================================

def binary_to_hex(binary_str):
    """
    Takes a 23-bit binary string (e.g. '00100000000011001000100'),
    pads it to 24 bits on the left ('000100000000011001000100'),
    and returns a 6-digit hex string ('010c84').
    """
    # Pad 1 leading zero to make it 24 bits
    padded_bin = binary_str.zfill(24)
    
    # Convert 24-bit binary string directly to 6-digit hex
    val = int(padded_bin, 2)
    return f"{val:06x}"

# ============================================================
# REGISTER PARSING
# ============================================================

def parse_register(register):

    register = register.strip().lower()

    if not register.startswith("$r"):
        raise ValueError(f"Invalid register: {register}")

    try:
        number = int(register[2:])
    except ValueError:
        raise ValueError(f"Invalid register: {register}")

    if number < 0 or number > 63:
        raise ValueError(f"Register out of range: {register}")

    return number


# ============================================================
# IMMEDIATE PARSING (6-bit Signed / Unsigned)
# ============================================================

def parse_immediate(value):

    value = int(value)

    if value < -32 or value > 31:
        raise ValueError(f"Immediate {value} does not fit in 6 bits")

    # Handle 2's complement for negative 6-bit values
    if value < 0:
        value = (1 << 6) + value

    return value & 0x3F


# ============================================================
# INSTRUCTION ENCODING (Returns 23-bit Binary)
# ============================================================

def encode_r_type_binary(op, operands):
    if len(operands) != 3:
        raise ValueError(f"{op} requires 3 registers")

    rd = parse_register(operands[0])
    rs = parse_register(operands[1])
    rt = parse_register(operands[2])

    opcode = OPCODES[op]

    value = (
        (opcode << 18) |
        (rs << 12) |
        (rt << 6) |
        rd
    )

    return f"{value:023b}"

def encode_i_type_binary(op, operands, labels):
    if len(operands) != 3:
        raise ValueError(f"{op} requires 3 operands")

    rt = parse_register(operands[0])
    rs = parse_register(operands[1])

    target = operands[2]

    if op in {"BEQ", "BNE"} and target in labels:
        immediate = parse_immediate(labels[target])
    else:
        immediate = parse_immediate(target)

    opcode = OPCODES[op]

    value = (
        (opcode << 18) |
        (rs << 12) |
        (rt << 6) |
        immediate
    )

    return f"{value:023b}"

def encode_j_type_binary(op, operands, labels):
    if len(operands) != 1:
        raise ValueError(f"{op} requires 1 target address")

    target = operands[0]

    if target in labels:
        address = labels[target]
    else:
        address = int(target)

    if address < 0 or address > (2**18 - 1):
        raise ValueError(f"Jump address out of range: {address}")

    opcode = OPCODES[op]

    value = (opcode << 18) | address

    return f"{value:023b}"


# ============================================================
# HELPER FUNCTIONS & PARSING
# ============================================================

def clean_line(line):
    if "#" in line:
        line = line.split("#")[0]
    return line.strip()


def parse_instruction(line):
    parts = line.replace(",", " ").split()
    if not parts:
        return None, []
    return parts[0].upper(), parts[1:]


def first_pass(lines):
    labels = {}
    instruction_address = 0

    for line_number, original_line in enumerate(lines, start=1):
        line = clean_line(original_line)
        if not line:
            continue

        while ":" in line:
            label, remainder = line.split(":", 1)
            label = label.strip()

            if not label:
                raise ValueError(f"Invalid label on line {line_number}")
            if label in labels:
                raise ValueError(f"Duplicate label: {label}")

            labels[label] = instruction_address
            line = remainder.strip()
            if not line:
                break

        if line:
            instruction_address += 1

    return labels


def second_pass(lines, labels):
    encoded_instructions = []

    for line_number, original_line in enumerate(lines, start=1):
        line = clean_line(original_line)
        if not line or ":" in line and not line.split(":", 1)[1].strip():
            continue

        if ":" in line:
            line = line.split(":", 1)[1].strip()

        try:
            operation, operands = parse_instruction(line)

            if operation not in OPCODES:
                raise ValueError(f"Unknown instruction: {operation}")

            if operation in R_TYPE:
                binary_code = encode_r_type_binary(operation, operands)
            elif operation in I_TYPE:
                binary_code = encode_i_type_binary(operation, operands, labels)
            elif operation in J_TYPE:
                binary_code = encode_j_type_binary(operation, operands, labels)
            else:
                raise ValueError(f"Unsupported instruction: {operation}")

            # Pass binary string to your separate function
            hex_code = binary_to_hex(binary_code)

            encoded_instructions.append((binary_code, hex_code))

        except Exception as error:
            raise ValueError(
                f"Error on line {line_number}: {original_line.strip()}\n{error}"
            )

    return encoded_instructions


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("======================================")
    print("      CSE332 GROUP 4 ASSEMBLER")
    print("======================================")

    input_file = input("Enter assembly filename (example: program.asm): ")

    with open(input_file, "r") as file:
        lines = file.readlines()

    labels = first_pass(lines)

    print("\nSymbol Table:")
    if labels:
        for label, address in labels.items():
            print(f"{label} -> instruction {address}")
    else:
        print("No labels found.")

    instructions = second_pass(lines, labels)

    print("\nMachine Code (BIN / HEX):")
    print("--------------------------------------")
    for i, (bin_inst, hex_inst) in enumerate(instructions):
        print(f"{i}: BIN={bin_inst}  HEX={hex_inst}")

    output_file = "output.hex"
    with open(output_file, "w") as file:
        file.write("v2.0 raw\n")
        for _, hex_inst in instructions:
            file.write(hex_inst + "\n")

    print("--------------------------------------")
    print(f"Assembled {len(instructions)} instructions.")
    print(f"Hexadecimal machine code written to {output_file}")
    print("======================================")


if __name__ == "__main__":
    main()