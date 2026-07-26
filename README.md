# crackme-algo-reversing

Writeup y keygen de un crackme en Delphi (compilado para Windows, `pei-i386`),
resuelto con GDB en Windows y un solver en Python que invierte el algoritmo
de validación por backtracking.

## El crackme

- Ejecutable Win32 (Delphi/C++Builder, sin símbolos de debug)
- Tiene un único campo de texto que valida una contraseña
- Al ingresar la contraseña correcta, se habilita el botón "Next"

## Proceso de reversing

1. **Debug con GDB** sobre el binario (terminal elevada, por el flag
   `requireAdministrator` del manifest)
2. Breakpoints en `GetWindowTextA` / `GetDlgItemTextA` para encontrar el
   momento en que el programa lee el texto ingresado
3. Se sigue la pila de llamadas hasta encontrar una **llamada indirecta a
   través de una VMT** (`call *0x21(%ebx)`, típica de cómo Delphi invoca
   los eventos `OnClick`/`OnChange`), que lleva al handler real del crackme
4. Dentro del handler (`0x4223b0`), se identifica:
   - Una función de **encoding** (`0x422cf4`) que transforma el input
     carácter por carácter, con un acumulador que depende de todos los
     caracteres anteriores, reducido módulo 90 al rango ASCII `'0'`-`'Z'`
   - Una **comparación final** contra un string fijo hardcodeado en el
     binario (`0x4223ee`)
5. El algoritmo se reimplementa en Python y se **invierte por backtracking**
   (se prueba cada carácter posible en cada posición) para encontrar
   contraseñas cuyo resultado coincida con el string objetivo

## Resultado

El algoritmo no es inyectivo (reduce el espacio de entrada a solo 43
valores de salida posibles por carácter), así que **la contraseña no es
única** — existen múltiples strings de 12 caracteres que desbloquean el
crackme por igual.

## Archivos

- `keygen_backtracker.py` — motor genérico de backtracking, reusable para
  cualquier crackme con el patrón "algoritmo custom + comparación contra
  target fijo". No conoce nada específico de este binario en particular.
- `delphi_serial_solver.py` — keygen de este crackme puntual: implementa
  el algoritmo específico (`step()`) sacado del disassemble y expone una
  CLI para generar seriales válidos.

## Uso

```bash
git clone https://github.com/dev-lang/crackme-algo-reversing.git
cd crackme-algo-reversing

# Generar un serial válido
python delphi_serial_solver.py

# Generar varios seriales distintos
python delphi_serial_solver.py --all 5

# Restringir el charset (por defecto prueba ASCII imprimible)
python delphi_serial_solver.py --charset alnum

# Probar contra otro target hardcodeado (por ejemplo, otra versión del crackme)
python delphi_serial_solver.py --target "OTRO-STRING"

# Solo el resultado, sin el banner
python delphi_serial_solver.py --quiet
```

## Adaptar a otro crackme

Si el algoritmo es distinto pero sigue el mismo patrón (encoding carácter
por carácter con estado acumulado + comparación contra un string fijo):

1. Desensamblá la función de validación del binario nuevo
2. Copiá `delphi_serial_solver.py`, y reescribí únicamente:
   - `step()` — con la lógica nueva encontrada en el disassemble
   - `DEFAULT_TARGET` — el string hardcodeado encontrado
3. Reusá `keygen_backtracker.py` tal cual — el motor de búsqueda no cambia

## Herramientas usadas

- GDB (vía MSYS2) para debugging del binario en Windows
- Python 3 para el solver / keygen

## Disclaimer

Resuelto con fines educativos, para practicar reversing (crackme
diseñado específicamente para este propósito).
