"""
Solver para el algoritmo de validacion del crackme (E:\\prueba\\crackme.exe)

Reversing realizado:
- Handler del evento de validacion en 0x4223b0
- Funcion de encoding del input en 0x422cf4
- Comparacion final en 0x4223ee (target hardcodeado en el binario)

El algoritmo aplica, para cada caracter de la contrasena (1-indexado como en Delphi),
un acumulador (edi) que depende de todos los caracteres anteriores, y despues reduce
el resultado modulo 90 hasta caer en el rango ASCII '0'-'Z' (0x30-0x5a).

Uso:
    python3 crackme_solver.py
    (o importa encode()/find_password() desde otro script)
"""

MOD = 90
CHAR_MIN = 0x30  # '0'
CHAR_MAX = 0x5a  # 'Z'


def reduce_val(v: int) -> int:
    """Reduce un valor de 32 bits al rango ASCII 0x30-0x5a, replicando
    exactamente el loop de 0x422d48-0x422d68 del binario."""
    v &= 0xFFFFFFFF
    while True:
        r = v % MOD
        v = r + 0x30 if r < CHAR_MIN else r
        if CHAR_MIN <= v <= CHAR_MAX:
            return v
        v &= 0xFFFFFFFF


def step(edi: int, c: int, i: int, length: int):
    """Un paso del algoritmo para el caracter c en la posicion i (1-indexada).
    Devuelve (edi_nuevo, caracter_de_salida)."""
    k = (length - i) & 0xFFFFFFFF
    edi_new = (edi * (1 + k) + c) & 0xFFFFFFFF
    ebx = (c * edi_new + i) & 0xFFFFFFFF
    return edi_new, reduce_val(ebx)


def encode(password: str) -> str:
    """Aplica el algoritmo del crackme a un string y devuelve el resultado
    codificado (lo que el binario compara contra el target hardcodeado)."""
    length = len(password)
    edi = 0
    out = []
    for idx, ch in enumerate(password):
        i = idx + 1
        edi, o = step(edi, ord(ch), i, length)
        out.append(chr(o))
    return ''.join(out)


def find_password(target: str, charset=range(0x20, 0x7f)):
    """Busca por backtracking un string de igual largo que 'target' cuyo
    encode() coincida exactamente. Devuelve el string encontrado o None."""
    length = len(target)
    solution = [None] * length

    def search(pos, edi):
        if pos == length:
            return True
        target_char = ord(target[pos])
        i = pos + 1
        for c in charset:
            edi_new, out = step(edi, c, i, length)
            if out == target_char:
                solution[pos] = c
                if search(pos + 1, edi_new):
                    return True
                solution[pos] = None
        return False

    if search(0, 0):
        return ''.join(chr(c) for c in solution)
    return None


if __name__ == "__main__":
    TARGET = "DD@2=?1U7>K2"  # string hardcodeado en 0x428864->+0x74

    password = find_password(TARGET)
    print("Target  :", TARGET)
    print("Password:", password)

    if password:
        print("Verificacion encode(password) == target:",
              encode(password) == TARGET)
