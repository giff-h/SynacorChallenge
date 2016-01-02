from readchar import readchar
from struct import unpack
import sys

max_num = 2 ** 15

memory = []
registers = [0 for _ in range(8)]
#registers[-1] = 1
stack = []
history = []
pc = 0

with open("callhistory", mode="w") as file:
    file.write("History\n")


def write_history():
    with open("callhistory", mode="a+") as file:
        for item in history:
            file.write(item + "\n")
        history.clear()


def register(r):
    return r % max_num


def register_value(r):
    if not is_register(r):
        raise Exception("bad register call")
    return registers[register(r)]


def is_register(r):
    return not register(r) == r


def value(n):
    return register_value(n) if is_register(n) else n


def chalt():
    """stop execution and terminate the program"""
    write_history()
    sys.exit(0)


def cset(a, b):
    """set register <a> to the value of <b>"""
    registers[register(a)] = value(b)


def cpush(a):
    """push <a> onto the stack"""
    stack.append(value(a))


def cpop(a):
    """remove the top element from the stack and write it into <a>; empty stack = error"""
    registers[register(a)] = stack.pop()


def ceq(a, b, c):
    """set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise"""
    registers[register(a)] = 1 if value(b) == value(c) else 0


def cgt(a, b, c):
    """set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise"""
    registers[register(a)] = 1 if value(b) > value(c) else 0


def cjmp(a):
    """jump to <a>"""
    return value(a)


def cjt(a, b):
    """if <a> is nonzero, jump to <b>"""
    return value(b) if not value(a) == 0 else None


def cjf(a, b):
    """if <a> is zero, jump to <b>"""
    return value(b) if value(a) == 0 else None


def cadd(a, b, c):
    """assign into <a> the sum of <b> and <c> (modulo 32768)"""
    registers[register(a)] = (value(b) + value(c)) % max_num


def cmult(a, b, c):
    """store into <a> the product of <b> and <c> (modulo 32768)"""
    registers[register(a)] = (value(b) * value(c)) % max_num


def cmod(a, b, c):
    """store into <a> the remainder of <b> divided by <c>"""
    registers[register(a)] = value(b) % value(c)


def cand(a, b, c):
    """stores into <a> the bitwise and of <b> and <c>"""
    registers[register(a)] = value(b) & value(c)


def cor(a, b, c):
    """stores into <a> the bitwise or of <b> and <c>"""
    registers[register(a)] = value(b) | value(c)


def cnot(a, b):
    """stores 15-bit bitwise inverse of <b> in <a>"""
    b = int(''.join(str((not bool(int(i))).real) for i in bin(value(b))[2:].rjust(15, '0')), 2)
    registers[register(a)] = b


def crmem(a, b):
    """read memory at address <b> and write it to <a>"""
    registers[register(a)] = value(memory[value(b)])


def cwmem(a, b):
    """write the value from <b> into memory at address <a>"""
    memory[value(a)] = value(b)


def ccall(a):
    """write the address of the next instruction to the stack and jump to <a>"""
    stack.append(pc + 2)
    return cjmp(a)


def cret():
    """remove the top element from the stack and jump to it; empty stack = halt"""
    if len(stack) == 0:
        chalt()
    else:
        return stack.pop()


def cout(a):
    """write the character represented by ascii code <a> to the terminal"""
    a = register_value(a) if is_register(a) else a
    print(chr(a), end='')


def cin(a):
    """read a character from the terminal and write its ascii code to <a>;
    it can be assumed that once input starts, it will continue until a newline is encountered;
    this means that you can safely read whole lines from the keyboard and trust that they will be fully read"""
    char = readchar()
    if char == "\r":
        char = "\n"
    cout(ord(char))
    history.append("input: " + repr(char))
    sys.stdout.flush()
    registers[register(a)] = ord(char)


def cnoop():
    """no operation"""
    pass


opcodes = [chalt, cset, cpush, cpop, ceq,
           cgt, cjmp, cjt, cjf, cadd,
           cmult, cmod, cand, cor, cnot,
           crmem, cwmem, ccall, cret, cout,
           cin, cnoop]
assert tuple(map(lambda meth: meth.__code__.co_argcount, opcodes)) == (0, 2, 1, 1, 3,
                                                                       3, 1, 2, 2, 3,
                                                                       3, 3, 3, 3, 2,
                                                                       2, 2, 1, 0, 1,
                                                                       1, 0)


if __name__ == "__main__":
    with open("challenge.bin", mode="rb") as file:
        memory = file.read()
    memory = [unpack('H', memory[i:i + 2])[0] for i in range(0, len(memory), 2)]
#    memory[521] = 8
#    memory[5451] = 7

    while True:
        instr = memory[pc]
        params = opcodes[instr].__code__.co_argcount
        params = memory[pc+1:pc+1+params]
        history.append(str(pc) + ": " + str(tuple([instr] + params)))
        if len(history) >= 10:
            write_history()
        next_pc = opcodes[instr](*params)
        pc = pc + len(params) + 1 if next_pc is None else next_pc
