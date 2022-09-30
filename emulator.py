'''
    - make inputs just set an area in memory
    - extend keyboard input to full standard keyboard
    - add argparser
'''

'''
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;            ISA                 ;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; all instructions are 3 bytes
; instruction, arg, arg

;;;;;;;;    moving data around
;   move        dest        src
;   loadk       regnum      const
;   mvadl       regnum              #set the low byte of the address register
;   mvadh       regnum              #set the high byte of the address register
;   load        regnum
;   store       regnum

;;;;;;;;    register math       
;   add         regnum      regnum
;   sub         regnum      regnum
;   neg         regnum      regnum
;   mul         regnum      regnum
;   div         regnum      regnum
;   mod         regnum      regnum
;   rshift      regnum      
;   lshift      regnum
;   and         regnum      regnum
;   or          regnum      regnum
;   xor         regnum      regnum
;   xand        regnum      regnum

;;;;;;;;    comparators
;   eq          regnum      regnum  ;  set flag
;   neq         regnum      regnum  ;  set flag
;   lt          regnum      regnum  ;  set flag
;   gt          regnum      regnum  ;  set flag
;   lte         regnum      regnum  ;  set flag
;   gte         regnum      regnum  ;  set flag

;;;;;;;;    control flow
; all jumps are only 7 bits, the first bit is the sign bit, max distance is 128; gonna be a lot of jumpin goin on

;   ijf                 ;   invert the jump flag bit
;   jmp         addr    ;   unconditional relative jump
;   cjmp        addr    ;   if flag is set

;   call        addr    ;   copies all registers to stack, adds pc to stack, jumps to addr
;   ret                 ;   pops pc from stack, pops all registers from stack, jumps to pc

;;;;;;;;    misc
;   nop
;   halt
'''


import argparse
from cmath import inf
import os
import random
import sys
from turtle import delay
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame import Vector2
from pygame.locals import (
    K_BACKQUOTE, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0, K_MINUS, K_EQUALS, K_BACKSPACE,
    K_TAB, K_q, K_w, K_e, K_r, K_t, K_y, K_u, K_i, K_o, K_p, K_LEFTBRACKET, K_RIGHTBRACKET, K_BACKSLASH,
    K_CAPSLOCK, K_a, K_s, K_d, K_f, K_g, K_h, K_j, K_k, K_l, K_SEMICOLON, K_QUOTE, K_RETURN,
    K_LSHIFT, K_z, K_x, K_c, K_v, K_b, K_n, K_m, K_COMMA, K_PERIOD, K_SLASH, K_RSHIFT,
    K_LCTRL, K_LALT, K_SPACE, K_RALT, K_RCTRL,
    K_UP, K_DOWN, K_LEFT, K_RIGHT,
    K_ESCAPE, K_F1, K_F2, K_F3, K_F4, K_F5, K_F6, K_F7, K_F8, K_F9, K_F10, K_F11, K_F12,
    K_PRINTSCREEN, K_SCROLLLOCK, K_PAUSE, K_INSERT, K_HOME, K_PAGEUP, K_DELETE, K_END, K_PAGEDOWN,
    K_NUMLOCK, K_KP_DIVIDE, K_KP_MULTIPLY, K_KP_MINUS, K_KP_PLUS, K_KP_ENTER, K_KP_PERIOD,
    K_KP0, K_KP1, K_KP2, K_KP3, K_KP4, K_KP5, K_KP6, K_KP7, K_KP8, K_KP9,
)

import logging
logging.basicConfig(level=logging.NOTSET)
LOG = logging.getLogger(":")
INSTRUCTION_LOGGING = False
CYCLE_LOGGING = True
CHECKING_KEYPRESS_LOGGING = True
# LOG.setLevel(logging.DEBUG)
# LOG.setLevel(logging.ERROR)

def fbhs(h):
    return "0x{:02x}".format(h)

def s8bnumfilter(num):
    if num > 127:
        num -= 256
    if num < -128:
        num += 256
    return num

class Emu:
    MEMORY_SIZE = 4096
    SCREEN_WIDTH = 64
    SCREEN_HEIGHT = 32

    def __init__(self):
        self.rom_loaded = False
        self.current_rom_path = None
        self.print_loaded_ops = True
        self.reset()
        self.isa = {
            # ;;;;;;;;    moving data around
            0x0000: self._move,     #dest        src
            0x0001: self._loadk,    #regnum      const
            0x0002: self._load,     #regnum      addr
            0x0003: self._store,    #regnum      addr

            # ;;;;;;;;    register math
            0x0004: self._add,      #regnum      regnum
            0x0005: self._sub,      #regnum      regnum
            0x0006: self._neg,      #regnum      regnum
            0x0007: self._mul,      #regnum      regnum
            0x0008: self._div,      #regnum      regnum
            0x0009: self._mod,      #regnum      regnum
            0x000a: self._rshift,   #regnum      
            0x000b: self._lshift,   #regnum
            0x000c: self._and,      #regnum      regnum
            0x000d: self._or,       #regnum      regnum
            0x000e: self._xor,      #regnum      regnum
            0x000f: self._xand,     #regnum      regnum

            # ;;;;;;;;    comparators
            0x0010: self._eq,       #regnum      regnum  ;  set flag
            0x0011: self._neq,      #regnum      regnum  ;  set flag
            0x0012: self._lt,       #regnum      regnum  ;  set flag
            0x0013: self._gt,       #regnum      regnum  ;  set flag
            0x0014: self._lte,      #regnum      regnum  ;  set flag
            0x0015: self._gte,      #regnum      regnum  ;  set flag

            # ;;;;;;;;    control flow
            # ; all jumps are only 7 bits, the first bit is the sign bit, max distance is 128; gonna be a lot of jumpin goin on
            
            0x0016: self._ijf,        #         ;   invert the jump flag bit
            0x0017: self._jmp,        # addr    ;   unconditional relative jump
            0x0018: self._cjmp,       # addr    ;   if flag is set

            0x0019: self._call,       #addr     ;   copies all registers to stack, adds pc to stack, jumps to addr
            0x001a: self._ret,        #         ;   pops pc from stack, pops all registers from stack, jumps to pc

            # ;;;;;;;;    misc
            0x001b: self._nop,
            0x001c: self._halt,
            0x001d: self._mvadl,    #set the low byte of the address register
            0x001e: self._mvadh,    #set the higher byte of the address register
        }

        # self.tone = pygame.mixer.Sound("tone.wav")

    def reset(self):
        LOG.info("reset")
        self._disp_clear()

        self.op = 0x00
        # self.key_inputs = [0] * 16
        self.memory = [0]*Emu.MEMORY_SIZE
        self.pc = 0x0200 #512 cant be set until after program load

        self.compare_flag = False
        self.carry = 0
        self.address_low = 0x00
        self.address_high = 0x00

        self.registers = [0x00]*16
        self.sound_timer = 0
        self.delay_timer = 0
        self.should_draw = False

        self.halted = False

        '''
        memory layout
            device  -   read only   -   keyboard_size - #   0x0000 - 0x00FF
            device  -   read/write  -   screen_size   - #   0x0100 - 0x0900   //  size: 64 * 32 = 2048 in hex: 0x800
            rom     -   read only   -   variable size - #   0x0901 - 0xZZZZ
            memory  -   read/write  -   variable size - #   0xZZZZ - 0xZZZZ

        not included:
            no stack // implement in software
        '''

        #   KEYBOARD INPUT DEVICE
        #   theres 101 keys so lets say 128 bits for the keys, 
        #   squish that later, but for now use 128 bytes
        #   0x0000 - 0x00FF
        self.keys = [   
            K_BACKQUOTE, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0, K_MINUS, K_EQUALS, K_BACKSPACE,
            K_TAB, K_q, K_w, K_e, K_r, K_t, K_y, K_u, K_i, K_o, K_p, K_LEFTBRACKET, K_RIGHTBRACKET, K_BACKSLASH,
            K_CAPSLOCK, K_a, K_s, K_d, K_f, K_g, K_h, K_j, K_k, K_l, K_SEMICOLON, K_QUOTE, K_RETURN,
            K_LSHIFT, K_z, K_x, K_c, K_v, K_b, K_n, K_m, K_COMMA, K_PERIOD, K_SLASH, K_RSHIFT,
            K_LCTRL, K_LALT, K_SPACE, K_RALT, K_RCTRL,
            K_UP, K_DOWN, K_LEFT, K_RIGHT,
            K_ESCAPE, K_F1, K_F2, K_F3, K_F4, K_F5, K_F6, K_F7, K_F8, K_F9, K_F10, K_F11, K_F12,
            K_PRINTSCREEN, K_SCROLLLOCK, K_PAUSE, K_INSERT, K_HOME, K_PAGEUP, K_DELETE, K_END, K_PAGEDOWN,
            K_NUMLOCK, K_KP_DIVIDE, K_KP_MULTIPLY, K_KP_MINUS, K_KP_PLUS, K_KP_ENTER, K_KP_PERIOD,
            K_KP0, K_KP1, K_KP2, K_KP3, K_KP4, K_KP5, K_KP6, K_KP7, K_KP8, K_KP9,
        ]
        self.key_map = {k: i for i, k in enumerate(self.keys)}

        if self.current_rom_path:
            self.load_rom(self.current_rom_path)

    def dump_mem(self):
        fname = "memory_dump.bin"
        with open(fname, "wb") as f:
            for byte in self.memory:
                f.write(bytes([byte]))

    def load_font(self):
        LOG.info("load font")
        for i in range(80):
            self.memory[i] = self.font[i]

    def load_rom(self, path):
        self.current_rom_path = path
        with open(path, "rb") as bin:
            rom = bin.read()

        bts = []
        bts_row = []
        rom_size = os.path.getsize(path)
        for i, b in enumerate(rom):
            hex_str = "0x{:02x}".format(b)
            bts_row.append(f"{hex_str} ")
            if ((i+1) % 16) == 0:
                bts.append(bts_row)
                bts_row = []
            self.memory[0x0200 + i] = b
        bts.append(bts_row)
        info_str = f"loading rom at {path}:" + "\n"+"\n".join(["".join(r) for r in bts])
        LOG.info(info_str)

        start = 0x0200
        end = 0x0200 + os.path.getsize(path)
        LOG.info(f"loaded rom into mem starting at {hex(start)} - to {hex(end)}")
        # except Exception as e:
        #     LOG.error("couldnt read rom")
        #     quit()

    def print_stack(self):
        stack_dump = []
        for ptr in self.stack:
            stack_dump.append(fbhs(ptr))
        stack_dump = ", ".join(stack_dump)
            
        LOG.info(f"======== stack_height: {len(self.stack)}") if CYCLE_LOGGING else None 
        LOG.info(f"======== stack: [{stack_dump}]") if CYCLE_LOGGING else None 

    def print_registers(self):
        reg_dump = []
        for ptr in self.registers:
            reg_dump.append(fbhs(ptr))
        reg_dump = ", ".join(reg_dump)
        LOG.info(f"======== registers: [{reg_dump}]") if CYCLE_LOGGING else None 
        
    def print_keys(self):
        key_dump = [" "]
        for y in range(0,4):
            line = []
            for x in range(4):
                i = (y*4) + x
                k = self.key_inputs[i]
                line.append(f"{k}")
            key_dump.append(", ".join(line))
        key_dump = "\t\t\n ".join(key_dump)
        LOG.info(f"======== keys: [{key_dump}]") if CYCLE_LOGGING else None 

    def inc_pc(self):
        self.pc += 3

    def cycle(self):
        LOG.info("========================= cycle ================================") if CYCLE_LOGGING else None 
        if self.pc >= Emu.MEMORY_SIZE:
            LOG.error("program counter exceeded program memory") if CYCLE_LOGGING else None 
            quit()

        self.op = self.memory[self.pc]
        self.vx = self.memory[self.pc + 1]
        self.vy = self.memory[self.pc + 2]
        if self.print_loaded_ops:
            LOG.info(f"======== pc: {fbhs(self.pc)}") if CYCLE_LOGGING else None 
            self.print_registers() if CYCLE_LOGGING else None 
            # self.print_stack() if CYCLE_LOGGING else None 
            # self.print_keys() if CYCLE_LOGGING else None
            LOG.info(f"======== current op: {fbhs(self.op)}") if CYCLE_LOGGING else None
        try:
            self.isa[self.op]()
        except:
            LOG.error(f"invalid instruction: 0x{self.op:02x}")
            quit()
        self.inc_pc()

        self.delay_timer = max(0, self.delay_timer - 1)
        self.sound_timer = max(0, self.sound_timer - 1)
        if self.sound_timer > 0:
            self.tone.play()

    def get_first_pressed_key(self):
        LOG.info("get_first_pressed_key") if INSTRUCTION_LOGGING else None 
        for i in range(16):
            if self.key_inputs[i] == 1:
                return i
        return -1

    def draw(self, pygame_surface):
        # LOG.info("draw")
        if self.should_draw:
            for i in range(2048):
                if self.screen_buffer[i] == 1:
                    x = i % Emu.SCREEN_WIDTH
                    y = int(i / Emu.SCREEN_WIDTH)
                    pygame_surface.set_at((x, y), (255, 255, 255))

    def handle_input_event(self, event):
        if event.key not in self.key_map:
            LOG.error("invalid  key")
            return
        if event.key in self.key_map:
            if event.type == pygame.KEYUP:
                LOG.info(f"key released: {pygame.key.name(event.key)}")
                key_mem_address = self.key_map[event.key]
                self.key_inputs[key_mem_address] = 0
            elif event.type == pygame.KEYDOWN:
                LOG.info(f"key pressed: {pygame.key.name(event.key)}")
                key_mem_address = self.key_map[event.key]
                self.key_inputs[key_mem_address] = 1

    # _move
    def _move(self):
        LOG.info("_move") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] = self.registers[self.vy]

    # _mvadl
    def _mvadl(self):
        LOG.info("_aldka") if INSTRUCTION_LOGGING else None 
        self.address_low = self.registers[self.vx]

    # _mvadh
    def _mvadh(self):
        LOG.info("_aldka") if INSTRUCTION_LOGGING else None 
        self.address_high = self.registers[self.vx]

    # _loadk
    def _loadk(self):
        LOG.info("_loadk") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] = self.vy

    # _load
    def _load(self):
        LOG.info("_load") if INSTRUCTION_LOGGING else None 
        address = self.address_low | (self.address_high << 8)
        self.registers[self.vx] = self.memory[address]

    # _store
    def _store(self):
        LOG.info("_store") if INSTRUCTION_LOGGING else None 
        address = self.address_low | (self.address_high << 8)
        self.memory[address] = self.registers[self.vx]

    # _add
    def _add(self):
        LOG.info("_add") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] += self.registers[self.vy]
        if self.registers[self.vx] > 0xff:
            self.carry = True
        self.registers[self.vx] &= 0xff

    # _sub
    def _sub(self):
        LOG.info("_sub") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] -= self.registers[self.vy]
        if self.registers[self.vx] < 0:
            self.carry = True
        self.registers[self.vx] &= 0xff

    # _neg
    def _neg(self):
        LOG.info("_neg") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] = -self.registers[self.vx]
        self.registers[self.vx] &= 0xff
        
    # _mul
    def _mul(self):
        LOG.info("_mul") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] *= self.registers[self.vy]
        if self.registers[self.vx] > 0xff:
            self.carry = True
        self.registers[self.vx] &= 0xff

    # _div
    def _div(self):
        LOG.info("_div") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] //= self.registers[self.vy]
        self.registers[self.vx] &= 0xff

    # _mod
    def _mod(self):
        LOG.info("_mod") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] %= self.registers[self.vy]
        self.registers[self.vx] &= 0xff

    # _rshift
    def _rshift(self):
        LOG.info("_rshift") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] >>= self.registers[self.vy]
        self.registers[self.vx] &= 0xff

    # _lshift
    def _lshift(self):
        LOG.info("_lshift") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] <<= self.registers[self.vy]
        self.registers[self.vx] &= 0xff

    # _and
    def _and(self):
        LOG.info("_and") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] &= self.registers[self.vy]
        self.registers[self.vx] &= 0xff

    # _or
    def _or(self):
        LOG.info("_or") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] |= self.registers[self.vy]
        self.registers[self.vx] &= 0xff

    # _xor
    def _xor(self):
        LOG.info("_xor") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] ^= self.registers[self.vy]
        self.registers[self.vx] &= 0xff

    # _xand
    def _xand(self):
        LOG.info("_xand") if INSTRUCTION_LOGGING else None 
        self.registers[self.vx] ^= self.registers[self.vy]
        self.registers[self.vx] &= 0xff

    # _eq
    def _eq(self):
        LOG.info("_eq") if INSTRUCTION_LOGGING else None 
        if self.registers[self.vx] == self.registers[self.vy]:
            self.registers[self.vx] = 1
            self.compare_flag = True
        else:
            self.registers[self.vx] = 0
            self.compare_flag = False

    # _neq
    def _neq(self):
        LOG.info("_neq") if INSTRUCTION_LOGGING else None 
        if self.registers[self.vx] != self.registers[self.vy]:
            self.registers[self.vx] = 1
            self.compare_flag = True
        else:
            self.registers[self.vx] = 0
            self.compare_flag = False

    # _lt
    def _lt(self):
        LOG.info("_lt") if INSTRUCTION_LOGGING else None 
        if self.registers[self.vx] < self.registers[self.vy]:
            self.registers[self.vx] = 1
            self.compare_flag = True
        else:
            self.registers[self.vx] = 0
            self.compare_flag = False

    # _gt
    def _gt(self):
        LOG.info("_gt") if INSTRUCTION_LOGGING else None 
        if self.registers[self.vx] > self.registers[self.vy]:
            self.registers[self.vx] = 1
            self.compare_flag = True
        else:
            self.registers[self.vx] = 0
            self.compare_flag = False
        
    # _lte
    def _lte(self):
        LOG.info("_lte") if INSTRUCTION_LOGGING else None 
        if self.registers[self.vx] <= self.registers[self.vy]:
            self.registers[self.vx] = 1
            self.compare_flag = True
        else:
            self.registers[self.vx] = 0
            self.compare_flag = False

    # _gte
    def _gte(self):
        LOG.info("_gte") if INSTRUCTION_LOGGING else None 
        if self.registers[self.vx] >= self.registers[self.vy]:
            self.registers[self.vx] = 1
            self.compare_flag = True
        else:
            self.registers[self.vx] = 0
            self.compare_flag = False

    # _ijf
    def _ijf(self):
        LOG.info("_ijf") if INSTRUCTION_LOGGING else None 
        self.compare_flag != self.compare_flag

    def post_jump_checks(self):
        assert self.pc >= 0
        assert self.pc < Emu.MEMORY_SIZE

    # _jmp
    def _jmp(self):
        LOG.info("_jmp") if INSTRUCTION_LOGGING else None 
        self.pc += self.vx
        self.post_jump_checks()

    # _cjmp
    def _cjmp(self):
        LOG.info("_cjmp") if INSTRUCTION_LOGGING else None 
        if self.compare_flag:
            self.pc += self.vx
            self.post_jump_checks()

    # _call
    # left unimplemented for now as can be done in software
    def _call(self):
        pass

    # _ret
    # left unimplemented for now as can be done in software
    def _ret(self):
        pass

    # _nop
    def _nop(self):
        LOG.info("_nop") if INSTRUCTION_LOGGING else None 
        pass

    # _halt
    def _halt(self):
        LOG.info("_halt") if INSTRUCTION_LOGGING else None 
        self.halted = True

    def _disp_clear(self):
        LOG.info("_disp_clear") if INSTRUCTION_LOGGING else None 
        self.screen_buffer = [0]*Emu.SCREEN_WIDTH*Emu.SCREEN_HEIGHT
        self.should_draw = True

def main():
    parser = argparse.ArgumentParser(description='Convert assembly code to machine code')
    parser.add_argument('file', nargs='?', default=sys.argv[1], help='input file')
    parser.add_argument('--no-keys', dest='keys', action='store_false', help='disable key input')
    args = parser.parse_args()

    pygame.init()
    screen_dims = Vector2(64, 32)
    window_dims = screen_dims * 16.0
    primary_surface = pygame.Surface(screen_dims)
    window = pygame.display.set_mode(window_dims)

    emu = Emu()
    emu.load_rom(args.file)

    dt = 1.0 / 60.0
    time = pygame.time.get_ticks()
    last_time = time
    running = True
    steps = 0
    max_steps = inf
    while running and steps <= max_steps and emu.halted == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            else:
                if event.type == pygame.KEYDOWN and event.key in [K_ESCAPE]:
                    running = False
                    break
                else:
                    if args.keys:
                        if event.type in [pygame.KEYUP, pygame.KEYDOWN]:
                            emu.handle_input_event(event)
                    
        if running == False:
            break

        # emu.dispatch_events()
        emu.cycle()

        primary_surface.fill((0, 0, 0))
        emu.draw(primary_surface)
        blit = pygame.transform.scale(
            primary_surface, window.get_size()
        )
        window.blit(blit, (0, 0))
        pygame.display.flip()

        time = pygame.time.get_ticks()
        dt = (time - last_time) / 1000.0
        last_time = time
        steps += 1
    pygame.quit()

if __name__ == "__main__":
    main()