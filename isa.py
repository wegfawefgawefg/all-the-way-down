isa = {
    0x0000: "move",     #dest-regnum src-regnum
    0x0001: "loadk",    #regnum      const
    0x0002: "load",     #regnum
    0x0003: "store",    #regnum
    0x0004: "add",      #regnum      regnum
    0x0005: "sub",      #regnum      regnum
    0x0006: "neg",      #regnum      regnum
    0x0007: "mul",      #regnum      regnum
    0x0008: "div",      #regnum      regnum
    0x0009: "mod",      #regnum      regnum
    0x000a: "rshift",   #regnum      
    0x000b: "lshift",   #regnum
    0x000c: "and",      #regnum      regnum
    0x000d: "or",       #regnum      regnum
    0x000e: "xor",      #regnum      regnum
    0x000f: "xand",     #regnum      regnum
    0x0010: "eq",       #regnum      regnum  ;  set flag
    0x0011: "neq",      #regnum      regnum  ;  set flag
    0x0012: "lt",       #regnum      regnum  ;  set flag
    0x0013: "gt",       #regnum      regnum  ;  set flag
    0x0014: "lte",      #regnum      regnum  ;  set flag
    0x0015: "gte",      #regnum      regnum  ;  set flag
    0x0016: "ijf",      #                    ;  invert the jump flag bit
    0x0017: "jmp",      #addr                ;  unconditional relative jump
    0x0018: "cjmp",     #addr                ;  conditional relative jump (if condition flag is 1)
    # 0x0019: "call",     #addr                ;  copies all registers to stack, adds pc to stack, jumps to addr
    # 0x001a: "ret",      #                    ;  pops pc from stack, pops all registers from stack, jumps to pc
    0x001b: "nop",
    0x001c: "halt",
    0x001d: "mvadl",    #regnum         #set the low byte of the address register
    0x001e: "mvadh",    #regnum         #set the higher byte of the address register
}

# invert isa to make it easier to look up opcodes
isa_inv = {v: k for k, v in isa.items()}