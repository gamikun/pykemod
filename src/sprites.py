from binascii import hexlify
from struct import unpack
import operator
import time




JP = 0xC3
JP_PE = 0xEA
NOP = 0x00
CP = 0xFE
CPL = 0x2F
CP_E = 0xBB
JR_Z = 0x28
JP_M = 0xFA
JR = 0x18
JR_NZ = 0x20
AND_L = 0xA5
AND_HL = 0xA6
DAA = 0x27
DI = 0xF3
EI = 0xFB
RET = 0xC9
RET_PO = 0xE0
RET_P = 0xF0
RRCA = 0x0F
RST_10h = 0xD7
RST_38h = 0xFF
LD_AB = 0x78
LD_A_D = 0x7A
LD_A_NN = 0x3A
LD_A_BC = 0x0A
LD_A_DE = 0x1A
LD_BC = 0x01
LD_DE_a = 0x12
LD_DE_NN = 0x11
LD_E = 0x1E
LD_E_L = 0x5D
LD_EH = 0x5C
LD_EC = 0x59
LD_SP = 0x31
LD_HE = 0x63
LD_HC = 0x61
LD_H_N = 0x26
LD_HL_NN = 0x2A
LD_HL_n = 0x36
LD_HL_a = 0x77
LD_LE = 0x6B
LD_NN_HL = 0x22
LD_d_n = 0x16
LD_D_A = 0x57
INC_B = 0x1B
LD_B = 0x06
LD_A = 0x3e
RLCA = 0x07
CALL = 0xCD
DEC_BC = 0x0B
DEC_HL = 0x35
OR_A_C = 0xB1
RRA = 0x1F
RLA = 0x17
ADC_A_L = 0x8D
ADD_A_D = 0x82
IX_INS = 0xDD
SBC_AE = 0x9B
EX_AF_AF = 0x08
CBITS = 0xCB
OUT = 0xD3
POP_BC = 0xC1
POP_DE = 0xD1

# Generics
CALL_cc_nn = 0xC4
INC_ss = 0x03
XOR_s = 0xB0
INC_r = 0x04
DEC_r = 0x05
ADD_HL_ss = 0x09
LD_dd_nn = 0x01
LD_r_r = 0x40
PUSH_qq = 0xC5

# Discovery masks
COND_MASK = 0xC7
PAIR_MASK = 0xCF
XOR_MASK = 0xF8
INC_MASK = 0x07
DEC_MASK = 0xC7
ADD_HL_ss_MASK = 0xCF
LD_dd_nn_MASK = 0xCF
LD_r_r_MASK = 0xC0
PUSH_qq_MASK = 0xCF

# Substractors
PAIR_INC_ss = 0x30
REG_XOR_s = 0x07
REG_INC_r = 0x38
REG_DEC_r = 0x38
REG_ADD_HL_ss = 0x30
REG_LD_dd_nn = 0x30
REG_LD_r_r = 0x40
REG_PUSH_qq = 0x30

O_MEM_SIZE = 0x0149
O_ROM_SIZE = 0x0148
O_CTR_TYPE = 0x0147

INT_ENABLED = True

B = 0
C = 1
D = 2
E = 3
H = 4
L = 5
A = 7
Z = 8
PV = 9
N = 10
S = 11
F = 12
P = 13

pair_tuples = [
    (B, C), (D, E),
    (H, L), (S, P),
]

pc = 0x0100
sp = 0
bc = 0
ix = 0
af = 0

CND_NZ = 0
CND_Z = 1
CND_NC = 2
CND_C = 3
CND_PO = 4
CND_PE = 5
CND_P = 6
CND_M = 7

PAIR_BC = 0
PAIR_DE = 1
PAIR_HL = 2
PAIR_SP = 3

cnd_names = ['nz', 'z', 'nc', 'c', 'po', 'pe', 'p', 'm']

with open('../PokemonRed.gb', 'rb') as fp:
    try:
        data = fp.read()
        
        #opcode = data[0x0150:0x0150+1000]

        memory_size = ord(data[O_MEM_SIZE])
        rom_size = ord(data[O_ROM_SIZE])
        catr_type = ord(data[O_CTR_TYPE])

        stack = bytearray(0xFFFFFF)

        print("Catridge type: {}".format(catr_type))
        print("RAM size: {}".format(memory_size))
        print("ROM size: {}".format(rom_size))

        
        #print("code: {}".format(hexlify(opcode)))
        reg = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        areg = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        while 1:
            opcode = ord(data[pc])
            opcode_mask = opcode & COND_MASK
            
            if opcode == NOP:
                print("nop")
                pc += 1

            elif opcode == JP:
                ope, = unpack('<H', data[pc + 1 : pc + 3])
                print("jp 0x{:04X}".format(ope))
                pc = ope

            elif opcode == JP_PE:
                oper, = unpack('<H', data[pc + 1 : pc + 3])
                
                print("jr pe, 0x{:04X}".format(oper))

                if reg[PV] % 2 == 0:
                    pc = oper
                else:
                    pc += 3

            elif opcode == CP:
                n = ord(data[pc + 1])
                print("cp 0x{:02X}".format(n))
                r = reg[A] - n
                reg[S] = r < 0
                reg[Z] = r == 0
                reg[N] = 1
                # TODO: ver que es borrow exactamente
                # reg[H] = #
                reg[C] = reg[A] < n

                pc += 2

            elif opcode == JR_Z:
                operand, = unpack('b', data[pc + 1])

                print("jr z,0x{:02X}".format(operand))
                
                if reg[Z]:
                    pc += operand + 2
                else:
                    pc += 2

            elif opcode == JR:
                operand = ord(data[pc + 1])
                print("jr 0x{:02X}".format(operand))
                pc += ord(data[pc + 1]) + 2

            elif opcode == DI:
                print("di")
                INT_ENABLED = False
                pc += 1

            elif opcode == RET_PO:
                print("ret po")
                if reg[PV]:
                    pc, = unpack('<H', stack[sp:sp + 2])
                else:
                    pc += 1

            elif opcode == RRCA:
                print("rrca")
                reg[A] = reg[A] >> 1
                pc += 1

            elif opcode == RST_38h:
                print("rst 38h")
                sp -= 1
                stack[sp] = (pc & 0xFF00) >> 8
                sp -= 1
                stack[sp] = pc & 0xFF
                pc = 0x1038 # ES 38 el correcto

            elif opcode == LD_BC:
                print("ld b,c")
                operand, = unpack('<H', data[pc + 1:pc + 3])
                bc = operand
                pc += 3

            elif opcode == LD_B:
                print("ld b")
                operand = ord(data[pc + 1])
                reg[B] = operand
                pc += 2

            elif opcode == RLCA:
                print("rlca")
                # TODO: Dudas, carry flag
                reg[A] = (reg[A] << 1) & 0xFF
                reg[C] = reg[A] & 0x80
                reg[A] = reg[A] | 0x01
                pc += 1

            elif opcode == LD_A:
                print("ld a")
                operand = ord(data[pc + 1])
                pc += 2

            elif opcode == CALL: # 0xCD
                ope, = unpack('<H', data[pc + 1:pc + 3])
                print("call 0x{:04X}".format(ope))
                sp -= 1
                stack[sp] = (0xFF00 & pc) >> 8
                sp -= 1
                stack[sp] = pc & 0xFF
                pc = ope

            elif opcode == LD_SP:
                sp, = unpack('<H', data[pc + 1:pc + 3])
                print(sp)
                pc += 3


            elif opcode == LD_HL_n:
                try:
                    ope = ord(data[pc + 1])
                    print("ld (hl), {:02X}H".format(ope))
                    stack[hl] = ope
                except IndexError:
                    print("index not found: {}".format(hl))
                    break
                pc += 2


            elif opcode == DEC_BC:
                bc -= 1
                print("dec b,c")
                pc += 1

            elif opcode == LD_AB:
                reg[A] = reg[B]
                print("ld b,a")
                pc += 1

            elif opcode == OR_A_C:
                reg[A] = reg[A] | reg[C]
                pc += 1

            elif opcode == JR_NZ:
                operand, = unpack('b', data[pc + 1])
                print("jr nz,0x{:02X}".format(operand))
                if not reg[Z]:
                    pc += operand + 2
                else:
                    pc += 2


            elif opcode == RRA:
                print("rra")
                new_c = reg[C]
                reg[C] = reg[A] & 0x01
                reg[A] = (reg[A] >> 1) + (new_c << 7)
                pc += 1

            elif opcode == DEC_HL:
                print("dec (hl)")
                # TODO: es (HL) ha yque ver la
                #       diferencia con HL.
                reg[PV] = stack[hl] == 0x7F
                nw = stack[hl] - 1
                reg[S] = nw < 0
                reg[Z] = nw == 0
                reg[H] = (reg[C] & 0b1000) >> 3 # TODO: arreglar
                reg[N] = 0
                if nw >= 0 and nw <= 255:
                    stack[hl] = nw
                pc += 1

            elif opcode == LD_HC:
                print("ld h,c")
                reg[H] = reg[C]
                pc += 1

            elif opcode == LD_HL_a:
                print("ld (hl),a")
                stack[hl] = reg[A]
                pc += 1

            elif opcode == ADC_A_L:
                print("ld a,l")
                # TODO: WHAT?
                reg[A] += reg[C] + reg[L]
                reg[S] = reg[A] < 0
                reg[Z] = reg[A] == 0
                reg[H] = (reg[C] & 0b1000) >> 3
                reg[C] = (reg[A] & 0x80) >> 7
                # TODo: Detecta overflow
                pc += 1

            elif opcode == EI:
                print("ei")
                INT_ENABLED = True
                pc += 1

            elif opcode == RST_10h:
                print("rst 10h")
                # TODO: PUSH TO THE STAck
                stack[sp] = 0x10
                pc += 1

            elif opcode == LD_EC:
                print("ld e,c")
                reg[E] = reg[C]
                pc += 1

            elif opcode == AND_L:
                print("and l")
                reg[A] = reg[A] & reg[L]
                reg[S] = reg[A] < 0
                reg[Z] = reg[A] == 0
                reg[H] = 1
                reg[PV] = 0
                reg[N] = 0
                reg[C] = 0
                pc += 1

            elif opcode == CP_E:
                print("cp e")
                r = reg[A] - reg[E]
                reg[S] = r < 0
                reg[Z] = r == 0
                reg[H] = (reg[C] & 0b1000) >> 3
                reg[PV] = 0 # TODO: no jarcodear
                reg[N] = 1
                # reg[C] PENDIENTE

                pc += 1

            elif opcode == IX_INS:
                # TODO: nada por ahora
                pc += 2
                #break

            elif opcode == LD_HE:
                print("ld h,e")
                reg[H] = reg[E]
                pc += 1

            elif opcode == SBC_AE:
                print("sbc a,e")
                r = reg[A] - reg[E] - reg[C]
                reg[S] = r < 0
                reg[Z] = r == 0
                #reg[H] =  # NO SE
                reg[PV] = 0 # TODO: HARDCODED
                reg[N] = 1
                #reg[C] = # WHAT?
                reg[A] = r

                pc += 1

            elif opcode == RET_P:
                print("ret p")
                if reg[S] >= 0:
                    sp += 1
                    pc = stack[sp]
                    sp += 1
                    pc += stack[sp] << 8    
                else:
                    pc += 1

            elif opcode == JP_M:
                oper, = unpack('<H', data[pc+1:pc+3])
                print("jp m,0x{:02X}".format(oper))
                if reg[S] >= 0:
                    pc = oper
                else:
                    pc += 1

            elif opcode == LD_E:
                reg[E] = ord(data[pc + 1])
                pc += 2

            elif opcode == LD_d_n:
                # TODO: ver si es signed o unsigned
                reg[D] = ord(data[pc + 1])
                pc += 2

            elif opcode == LD_DE_a:
                loc = reg[D] + (reg[E] << 8)
                stack[loc] = reg[A]
                pc += 1

            elif opcode == RLA:
                old_c = reg[C]
                reg[C] = reg[A] & 0x80
                reg[A] = (reg[A] << 1) | old_c # estara bien?
                pc += 1

            elif opcode == AND_HL:
                reg[A] = reg[A] & stack[hl]
                reg[C] = 0
                reg[N] = 0
                reg[PV] = reg[A] % 2 == 0
                reg[H] = 1
                reg[Z] = reg[A] == 0
                reg[S] = reg[A] < 0
                pc += 1

            elif opcode == INC_B:
                reg[B] += 1
                # TODO: actualizar registrosc
                pc += 1

            elif opcode == LD_A_DE:
                loc = reg[D] + (reg[E] << 8)
                reg[A] = stack[loc]
                pc += 1

            elif opcode == LD_A_BC:
                loc = reg[B] + (reg[C] << 8)
                reg[A] = stack[loc]
                pc += 1

            elif opcode == LD_EH:
                reg[E] = reg[H]
                pc += 1

            elif opcode == LD_LE:
                print("ld l,e")
                reg[E] = reg[L]
                pc += 1

            elif opcode == ADD_A_D:
                print("add a,d")
                reg[A] = reg[A] + reg[D]
                pc += 1

            elif opcode == CPL:
                print("cpl")
                # estara correcto?
                reg[A] = ~reg[A] & 0xFF
                reg[N] = 1
                reg[H] = 1

                pc += 1

            elif opcode == LD_H_N:
                ope = ord(data[pc + 1])
                print("ld h,0x{:02X}".format(ope))
                reg[H] = ope
                pc += 2

            elif opcode == LD_A_NN:
                loc, = unpack('<H', data[pc + 1:pc + 3])
                print("ld a,(0x{:04X})".format(loc))
                reg[A] = stack[loc]
                pc += 3

            elif opcode == LD_E_L:
                print("ld e,l")
                reg[L] = reg[E]
                pc += 1

            elif opcode == EX_AF_AF:
                print("ex af,af'")
                new_a = reg[A]
                new_f = reg[F]
                reg[A] = areg[A]
                reg[F] = areg[F]
                areg[A] = new_a
                areg[F] = new_f
                pc += 1

            elif opcode == DAA:
                print("daa")
                if (reg[A] & 0xF) > 9 or reg[H]:
                    reg[A] += 0x06
                if ((reg[A] & 0xF0) >> 4) > 9 or reg[C]:
                    reg[A] += 0x60
                    reg[C] = 1
                reg[PV] = reg[A] % 2 == 0
                reg[Z] = reg[A] == 0
                pc += 1

            elif opcode == CBITS: # 0xCB
                bop = ord(data[pc + 1])
                if bop == 0x46:
                    loc = reg[L] + (reg[H] << 8)
                    reg[Z] = stack[loc] & 0x01
                    reg[N] = 0
                    reg[H] = 1
                    print("bit 0,(hl)")
                    pc += 2
                elif bop == 0x86:
                    loc = reg[L] + (reg[H] << 8)
                    stack[loc] = stack[loc] & 0xFE
                    print("res 0,(hl)")
                    pc += 2
                else:
                    print("bit desconocido: {:02X}".format(bop))
                    break

            elif opcode == OUT: # 0xD3
                ope = ord(data[pc + 1])
                print("out (0x{:02X}),a".format(ope))
                pc += 2

            elif opcode == LD_DE_NN: # 0x11
                ope, = unpack('<H', data[pc + 1:pc + 3])
                print("ld de,0x{:04X}".format(ope))
                reg[D] = ope & 0xFF
                reg[E] = (ope & 0xFF00) >> 8
                pc += 1

            elif opcode == LD_HL_NN: # 0x2A
                loc, = unpack('<H', data[pc + 1:pc + 3])
                print("ld hl,(0x{:04X})".format(ope))
                reg[L] = stack[loc]
                reg[H] = stack[loc + 1]
                pc += 3

            elif opcode == POP_BC: # 0xC1
                print("pop bc")
                reg[C] = stack[sp]
                sp += 1
                reg[B] = stack[sp]
                sp += 1
                pc += 1

            elif opcode == LD_D_A: # 0x57
                print("ld d,a")
                reg[D] = reg[A]
                pc += 1
                print(opcode)

            elif opcode == LD_A_D: # 0x7A
                print("ld a,d")
                reg[A] = reg[D]
                pc += 1

            elif opcode == LD_NN_HL: #0x22
                ope, = unpack('<H', data[pc + 1:pc + 3])
                print("ld (0x{:04X}),hl".format(ope))
                stack[ope] = hl & 0xFF
                stack[ope + 1] = (hl & 0xFF00) >> 8
                pc += 3

            elif opcode == POP_DE: # 0xD1
                print("pop de")
                reg[E] = stack[sp]
                sp += 1
                reg[D] = stack[sp]
                sp += 1
                pc += 1

            elif opcode == RET: # 0xC9
                print("ret")
                pc = stack[sp]
                sp += 1
                pc += stack[sp] << 8

            elif opcode_mask == CALL_cc_nn:
                cond = (opcode & 0b111000) >> 3
                ope, = unpack('<H', data[pc + 1:pc + 3])

                valid = 0
                if cond == CND_NZ:
                    valid = not reg[Z]
                elif cond == CND_Z:
                    valid = reg[Z]
                elif cond == CND_NC:
                    valid = not reg[C]
                elif cond == CND_C:
                    valid = reg[Z]
                elif cond == CND_PO:
                    valid = not reg[PV]
                elif cond == CND_PE:
                    valid = reg[PV]
                elif cond == CND_P:
                    valid = reg[S]
                else: # == CND_M (7)
                    valid = not reg[S]

                pc += 3
                if valid:
                    print("call {},0x{:04X}".format(cnd_names[cond], ope))
                    sp -= 1
                    stack[sp] = (0xFF00 & pc) >> 8
                    sp -= 1
                    stack[sp] = pc & 0xFF
                    pc = ope

            elif (opcode & PAIR_MASK) == INC_ss:
                pair = (opcode & PAIR_INC_ss) >> 4
                index_a, index_b = pair_tuples[pair]
                value = reg[index_a] + (reg[index_b] << 8) + 1
                reg[index_a] = (value & 0xFF)
                reg[index_b] = (value & 0xFF00) >> 8
                pc += 1

            elif (opcode & XOR_MASK) == XOR_s:
                print("xor")
                r = (opcode & REG_XOR_s)
                reg[A] = operator.xor(reg[r], reg[A])
                reg[S] = reg[A] < 0
                reg[Z] = reg[A] == 0
                reg[H] = 0
                reg[PV] = reg[A] % 2 == 0
                reg[N] = 0
                reg[C] = 0
                pc += 1

            elif opcode == 0xAF: # XOR a
                # Este es un caos especial porque al parecer
                # no esta del todo documentado.
                reg[A] = operator.xor(reg[A], reg[A])
                reg[S] = reg[A] < 0
                reg[Z] = reg[A] == 0
                reg[H] = 0
                reg[PV] = reg[A] % 2 == 0
                reg[N] = 0
                reg[C] = 0
                pc += 1

            elif opcode == 0xAA: # XOR d
                # Este es un caos especial porque al parecer
                # no esta del todo documentado.
                reg[A] = operator.xor(reg[A], reg[D])
                reg[S] = reg[A] < 0
                reg[Z] = reg[A] == 0
                reg[H] = 0
                reg[PV] = reg[A] % 2 == 0
                reg[N] = 0
                reg[C] = 0
                pc += 1

            elif opcode == 0xAD: # XOR L
                # Este es un caos especial porque al parecer
                # no esta del todo documentado.
                reg[A] = operator.xor(reg[A], reg[L])
                reg[S] = reg[A] < 0
                reg[Z] = reg[A] == 0
                reg[H] = 0
                reg[PV] = reg[A] % 2 == 0
                reg[N] = 0
                reg[C] = 0
                pc += 1

            elif (opcode & INC_MASK) == INC_r:
                r = (opcode & REG_INC_r) >> 3
                reg[PV] = reg[r] == 0x7F
                reg[r] += 1
                reg[S] = reg[r] < 0
                reg[Z] = reg[r] == 0
                reg[H] = (reg[C] & 0x08) >> 3
                reg[N] = 0
                pc += 1

            elif (opcode & DEC_MASK) == DEC_r:
                r = (opcode & REG_DEC_r) >> 3
                if r == 0x06: # (HL)
                    # TODO: arreglar
                    loc = (reg[H] << 8) + reg[L]
                    stack[loc] -=1 # TODO: tal vez son 2 bytes
                    pass
                else:
                    reg[PV] = reg[r] == 0x80
                    reg[r] -= 1
                    reg[S] = reg[r] < 0
                    reg[Z] = reg[r] == 0
                    #reg[H] = reg[B] & 0x10 TODO: TALVEZ
                    reg[N] = 1
                pc += 1

            elif (opcode & ADD_HL_ss_MASK) == ADD_HL_ss:
                break
                """
                print("add hl,hl")
                r = hl * 2
                hl = r
                reg[H] = (reg[C] & 0b10000000000) >> 11 # TODO: Talvez
                reg[N] = 0
                reg[C] = (r & 0x8000) >> 3 # TODO: arreglar
                pc += 1"""

            elif (opcode & LD_dd_nn_MASK) == LD_dd_nn:
                r1, r2 = pair_tuples[(opcode & REG_LD_dd_nn) >> 4]
                reg[r1] = ord(data[pc + 1])
                reg[r2] = ord(data[pc + 2])
                pc += 3

            elif (opcode & LD_r_r_MASK) == LD_r_r:
                r1 = (opcode & 0x38) >> 3
                r2 = opcode & 0x07
                if r2 == 0x06:
                    loc = reg[L] + (reg[H] << 8)
                    reg[r1] = stack[loc]
                    break
                else:
                    reg[r1] = reg[r2]

                pc += 1

            elif (opcode & PUSH_qq_MASK) == PUSH_qq:
                pair = (opcode & REG_PUSH_qq) >> 4
                r1, r2 = pair

                print("push af")
                sp -= 1
                stack[sp] = reg[r2]
                sp -= 1
                stack[sp] = reg[r1]
                pc += 1
                break

            else:
                print("BYE: {} ({})".format(hex(opcode), hex(pc)))
                print(bin(opcode))
                break

            time.sleep(0.018)

    except KeyboardInterrupt:
        print(hexlify(stack[-100:]))



