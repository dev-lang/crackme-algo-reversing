"""
Solver especifico para el algoritmo de validacion del crackme (E:\\prueba\\crackme.exe)

Reversing realizado:
- Handler del evento de validacion en 0x4223b0
- Funcion de encoding del input en 0x422cf4
- Comparacion final en 0x4223ee (target hardcodeado en el binario)

Esta parte es la UNICA especifica de este crackme: la funcion step()
reproduce exactamente las instrucciones de 0x422cf4. Todo lo demas
(busqueda, backtracking, generacion de multiples soluciones) vive en
keygen_backtracker.py y es reusable para otros crackmes.

Uso:
    python3 delphi_serial_solver.py
    python3 delphi_serial_solver.py --target "OTRO-STRING-HARDCODEADO"
    python3 delphi_serial_solver.py --target "..." --all 10
    python3 delphi_serial_solver.py --target "..." --charset alnum
"""

import argparse
import string

from keygen_backtracker import (
    find_password,
    find_all_passwords,
    count_candidates_first_position,
)

MOD = 90
CHAR_MIN = 0x30  # '0'
CHAR_MAX = 0x5a  # 'Z'

DEFAULT_TARGET = "DD@2=?1U7>K2"  # string hardcodeado en 0x428864 -> +0x74

CHARSETS = {
    "printable": range(0x20, 0x7f),
    "alnum": [ord(c) for c in string.ascii_letters + string.digits],
    "ascii_range": range(0x30, 0x5b),  # el mismo rango que usa la salida del algoritmo
}


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
    """Un paso del algoritmo de ESTE crackme para el caracter c en la
    posicion i (1-indexada). Devuelve (edi_nuevo, caracter_de_salida).

    Esta es la funcion a REESCRIBIR cuando adaptes el script a un
    crackme distinto -- todo lo demas se puede dejar igual."""
    k = (length - i) & 0xFFFFFFFF
    edi_new = (edi * (1 + k) + c) & 0xFFFFFFFF
    ebx = (c * edi_new + i) & 0xFFFFFFFF
    return edi_new, reduce_val(ebx)


def encode(password: str) -> str:
    """Corre el algoritmo hacia adelante (util para verificar candidatos)."""
    length = len(password)
    edi = 0
    out = []
    for idx, ch in enumerate(password):
        i = idx + 1
        edi, o = step(edi, ord(ch), i, length)
        out.append(chr(o))
    return ''.join(out)


def main():
    parser = argparse.ArgumentParser(
        description="Keygen solver para el algoritmo de este crackme (Delphi)")
    parser.add_argument("--target", default=DEFAULT_TARGET,
                         help="String hardcodeado contra el que compara el binario")
    parser.add_argument("--charset", default="printable",
                         choices=CHARSETS.keys(),
                         help="Conjunto de caracteres a probar para la contrasena")
    parser.add_argument("--all", type=int, metavar="N", default=None,
                         help="En vez de una sola, mostrar N contrasenas validas distintas")
    args = parser.parse_args()

    charset = CHARSETS[args.charset]

    if args.all:
        print(f"Buscando {args.all} contrasenas validas para target={args.target!r}\n")
        for i, pw in enumerate(find_all_passwords(args.target, step, charset, limit=args.all), start=1):
            ok = encode(pw) == args.target
            print(f"  {i}. {pw!r}  (encode == target: {ok})")
        return

    password = find_password(args.target, step, charset)
    print("Target  :", args.target)
    print("Password:", password)
    if password:
        print("Verificacion encode(password) == target:", encode(password) == args.target)

    print()
    print("Candidatos posibles solo para la primera posicion:",
          count_candidates_first_position(args.target, step, charset))
    print("(si hay mas de uno, la contrasena NO es unica)")


if __name__ == "__main__":
    main()
