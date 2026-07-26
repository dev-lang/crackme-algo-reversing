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


BANNER = r"""
   ______           __              ___
  / ____/________ _/ /______ ____  / _ \___ __ _____
 / /   / ___/ __ `/ //_/ __ `/ __ \/ , _/ -_) |/ / -_)
/ /___/ /  / /_/ / ,< / /_/ / / / /_/|_|\__/|___/\__/
\____/_/   \__,_/_/|_|\__,_/_/ /_/

           Delphi TEdit serial algo -- keygen
           algoritmo invertido via GDB + backtracking
"""

DIVIDER = "-" * 56


def _print_result(password: str, target: str):
    print(DIVIDER)
    print(f"  [+] Serial encontrado : {password}")
    print(f"  [+] Target            : {target}")
    print(f"  [+] Valido             : {'SI' if encode(password) == target else 'NO'}")
    print(DIVIDER)


def main():
    parser = argparse.ArgumentParser(
        description="Keygen para el algoritmo de este crackme (Delphi)")
    parser.add_argument("--target", default=DEFAULT_TARGET,
                         help="String hardcodeado contra el que compara el binario")
    parser.add_argument("--charset", default="printable",
                         choices=CHARSETS.keys(),
                         help="Conjunto de caracteres a probar para la contrasena")
    parser.add_argument("--all", type=int, metavar="N", default=None,
                         help="Generar N seriales validos distintos en vez de uno solo")
    parser.add_argument("--quiet", action="store_true",
                         help="No mostrar el banner, solo el serial")
    args = parser.parse_args()

    charset = CHARSETS[args.charset]

    if not args.quiet:
        print(BANNER)

    if args.all:
        print(f"  Generando {args.all} seriales validos...\n")
        print(DIVIDER)
        for i, pw in enumerate(find_all_passwords(args.target, step, charset, limit=args.all), start=1):
            print(f"  [{i:>2}] {pw}")
        print(DIVIDER)
        return

    password = find_password(args.target, step, charset)
    if password is None:
        print("  [!] No se encontro ningun serial valido con este charset.")
        return

    _print_result(password, args.target)

    candidates = count_candidates_first_position(args.target, step, charset)
    if len(candidates) > 1:
        print(f"  (nota: el serial no es unico -- {len(candidates)} opciones "
              f"posibles solo para el primer caracter)")


if __name__ == "__main__":
    main()
