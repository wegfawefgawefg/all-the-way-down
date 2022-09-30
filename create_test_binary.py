ops = [
    0x0000,
    0x1204, #   jump to 0x204 in memory, which means next op
    0x2206, #   store pc on stack and jump to 206
    0x3000, #   skips the next bc reg[0] and 00 are equal
    0x0000, #   should get skipped by above
    0x6001, #   should put a 1 in reg[0]
    0x4000, 
    0x0000, #   should get skipped by above

    #   testing 0x5000 and 0x6000
    0x6102, #   put a 2 in reg[0]
    0x6203, #   put a 2 in reg[0]
    0x5010, #   should not skip since reg[0] != reg[1]
    0x0000, #   should not get skipped by above
    0x6101, #   put a 1 in reg[0]
    0x5010, #   should skip since reg[0] == reg[1]
    0x0000, #   should get skipped by above
    0x6311, #   load 0x11 into reg[3]

    #####   testing 0x7000     #####
    #   should increment reg[0] 3 times
    0x7001,
    0x7001,
    0x7001,
    #   should add 5 to reg[1]
    0x7105,

    #####   testing 0x8000s     #####
    #   testing 0x8000
    0x60FE, #   put a FE in reg[0]
    0x6102, #   put a 02 in reg[1]
    0x8010, #   should set reg[0] to reg[1]
    #   testing 0x8001
    0x6000, #   put a 0 in reg[0]
    0x6101, #   put a 1 in reg[1]
    0x8011, #   should set reg[0] to 1

    #   testing 0x8002
    0x6001, #   put a 1 in reg[0]
    0x6102, #   put a 2 in reg[1]
    0x8012, #   should set reg[0] to 3

    #   testing 0x8003
    0x6001, #   put a 1 in reg[0]
    0x6101, #   put a 1 in reg[1]
    0x8013, #   should set reg[0] to 0
    0x8013, #   should set reg[0] to 1

    #   testing 0x8004
    0x60FE, #   put a FE in reg[0]
    0x6102, #   put a 2 in reg[1]
    0x8014, #   should set reg[0] to 1, reg[0xF] should be 1

    #   testing 0x8005
    0x6000, #   put a 0 in reg[0]
    0x6101, #   put a 1 in reg[1]
    0x8015, #   should set reg[0] to FF, reg[0xF] should be 0

    #   testing 0x8006
    0x6002, #   put a 2 in reg[0]
    0x8006, #   should set reg[0] to FF, reg[0xF] should be 1

    #   testing 0x8007
    0x6002, #   put a 2 in reg[0]
    0x6101, #   put a 1 in reg[1]
    0x8017, #   should set reg[0] to FF, reg[0xF] should be 1

    #   testing 0x8XYE
    0x6002, #   put a 2 in reg[0]
    0x6101, #   put a 1 in reg[1]
    0x8017, #   should set reg[0] to FF, reg[0xF] should be 1

    0x00FD, #   terminate
    # 0x800F,
    # 0x9000,
    # 0xA000,
    # 0xB000,
    # 0xC000,
    # 0xD000,
    # 0xE000,
    # 0xF000,
    # 0xF007,
    # 0xF00A,
    # 0xF015,
    # 0xF018,
    # 0xF01E,
    # 0xF029,
    # 0xF033,
    # 0xF055,
    # 0xF065,
]

fname = "test.bin"
with open(fname, "wb") as f:
    for op in ops:
        p1 = (op & 0xFF00) >> 8
        p2 = op & 0x00FF
        f.write(bytes([p1]))
        f.write(bytes([p2]))