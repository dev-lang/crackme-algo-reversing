"""
Motor generico de backtracking para resolver crackmes tipo:

    encode(input) == target_hardcodeado

Este modulo NO conoce el algoritmo especifico de ningun crackme puntual.
Vos le pasas una funcion `step(edi, c, i, length) -> (edi_nuevo, char_salida)`
que reproduce, para UN caracter en la posicion i (1-indexada), lo que hace el
disassemble del crackme que estes analizando. El motor se encarga de:

- Probar cada caracter posible en cada posicion
- Arrastrar el estado (edi / acumulador / lo que sea) entre posiciones
- Hacer backtracking si una eleccion no lleva a ninguna solucion
- Devolver una, varias, o todas las contrasenas validas

Para adaptarlo a un crackme nuevo:
    1. Desensamblá la funcion de validacion / encoding
    2. Reescribi SOLO la funcion `step()` para que replique esas instrucciones
    3. Reusa find_password() / find_all_passwords() tal cual estan aca
"""

from typing import Callable, Iterable, Iterator, Optional

# step(edi, c, i, length) -> (edi_nuevo, char_salida_como_int)
StepFn = Callable[[int, int, int, int], tuple]


def find_password(target: str, step: StepFn,
                   charset: Iterable[int] = range(0x20, 0x7f),
                   initial_state: int = 0) -> Optional[str]:
    """Devuelve la PRIMERA contrasena de igual largo que 'target' cuyo
    encode() (definido implicitamente por step) coincide exactamente."""
    length = len(target)
    solution = [None] * length

    def search(pos, state):
        if pos == length:
            return True
        target_char = ord(target[pos])
        i = pos + 1
        for c in charset:
            new_state, out = step(state, c, i, length)
            if out == target_char:
                solution[pos] = c
                if search(pos + 1, new_state):
                    return True
                solution[pos] = None
        return False

    if search(0, initial_state):
        return ''.join(chr(c) for c in solution)
    return None


def find_all_passwords(target: str, step: StepFn,
                        charset: Iterable[int] = range(0x20, 0x7f),
                        initial_state: int = 0,
                        limit: Optional[int] = None) -> Iterator[str]:
    """Generador: va devolviendo TODAS las contrasenas validas (o hasta
    'limit' si se especifica). Sirve para ver si la solucion es unica."""
    length = len(target)
    solution = [None] * length
    count = 0

    def search(pos, state):
        nonlocal count
        if limit is not None and count >= limit:
            return
        if pos == length:
            count += 1
            yield ''.join(chr(c) for c in solution)
            return
        target_char = ord(target[pos])
        i = pos + 1
        for c in charset:
            new_state, out = step(state, c, i, length)
            if out == target_char:
                solution[pos] = c
                yield from search(pos + 1, new_state)
                if limit is not None and count >= limit:
                    return

    yield from search(0, initial_state)


def count_candidates_first_position(target: str, step: StepFn,
                                     charset: Iterable[int] = range(0x20, 0x7f),
                                     initial_state: int = 0):
    """Cuenta rapido cuantos caracteres de entrada producen el primer
    caracter esperado (edi/estado inicial). Buen indicador de si el
    algoritmo tiene colisiones (o sea, de si la clave NO es unica)."""
    length = len(target)
    matches = []
    for c in charset:
        _, out = step(initial_state, c, 1, length)
        if out == ord(target[0]):
            matches.append(chr(c))
    return matches
