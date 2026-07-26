"""
Interfaz grafica (Tkinter) para el keygen del crackme.

Requiere que delphi_serial_solver.py y keygen_backtracker.py esten
en la misma carpeta que este archivo.

Uso:
    python gui.py

No necesita instalar nada aparte: Tkinter viene incluido con la
instalacion estandar de Python en Windows.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from delphi_serial_solver import (
    step,
    encode,
    DEFAULT_TARGET,
    CHARSETS,
)
from keygen_backtracker import find_password, find_all_passwords, count_candidates_first_position


class KeygenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Delphi Serial Keygen")
        self.geometry("520x420")
        self.resizable(False, False)

        self._build_widgets()

    def _build_widgets(self):
        pad = {"padx": 10, "pady": 5}

        title = tk.Label(self, text="Delphi TEdit Serial Keygen",
                          font=("Consolas", 14, "bold"))
        title.pack(pady=(12, 0))

        subtitle = tk.Label(self, text="algoritmo invertido via GDB + backtracking",
                             font=("Consolas", 9), fg="gray30")
        subtitle.pack(pady=(0, 10))

        form = tk.Frame(self)
        form.pack(fill="x", **pad)

        # Target
        tk.Label(form, text="Target (string hardcodeado):").grid(row=0, column=0, sticky="w")
        self.target_var = tk.StringVar(value=DEFAULT_TARGET)
        tk.Entry(form, textvariable=self.target_var, width=40).grid(row=0, column=1, sticky="we", padx=5)

        # Charset
        tk.Label(form, text="Charset:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.charset_var = tk.StringVar(value="printable")
        charset_combo = ttk.Combobox(form, textvariable=self.charset_var,
                                      values=list(CHARSETS.keys()), state="readonly", width=20)
        charset_combo.grid(row=1, column=1, sticky="w", padx=5, pady=(8, 0))

        # Cantidad
        tk.Label(form, text="Cantidad de claves:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.count_var = tk.IntVar(value=1)
        tk.Spinbox(form, from_=1, to=100, textvariable=self.count_var, width=10).grid(
            row=2, column=1, sticky="w", padx=5, pady=(8, 0))

        form.columnconfigure(1, weight=1)

        # Boton generar
        self.generate_btn = tk.Button(self, text="Generar Clave", font=("Consolas", 11, "bold"),
                                       bg="#2e7d32", fg="white", command=self.on_generate)
        self.generate_btn.pack(pady=12, ipadx=10, ipady=4)

        # Output
        output_frame = tk.Frame(self)
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tk.Label(output_frame, text="Resultado:").pack(anchor="w")

        text_container = tk.Frame(output_frame)
        text_container.pack(fill="both", expand=True)

        self.output_text = tk.Text(text_container, height=12, font=("Consolas", 10),
                                    bg="#1e1e1e", fg="#c8f7c5", wrap="word")
        scrollbar = tk.Scrollbar(text_container, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Boton copiar
        copy_btn = tk.Button(self, text="Copiar al portapapeles", command=self.on_copy)
        copy_btn.pack(pady=(0, 10))

    def on_generate(self):
        target = self.target_var.get().strip()
        if not target:
            messagebox.showwarning("Falta el target", "Ingresa el string target.")
            return

        charset_name = self.charset_var.get()
        charset = CHARSETS[charset_name]
        count = self.count_var.get()

        self.output_text.delete("1.0", tk.END)

        try:
            if count <= 1:
                password = find_password(target, step, charset)
                if password is None:
                    self.output_text.insert(tk.END, "No se encontro ninguna clave valida con este charset.\n")
                    return
                valido = encode(password) == target
                self.output_text.insert(tk.END, f"Serial encontrado : {password}\n")
                self.output_text.insert(tk.END, f"Target            : {target}\n")
                self.output_text.insert(tk.END, f"Valido            : {'SI' if valido else 'NO'}\n\n")

                candidatos = count_candidates_first_position(target, step, charset)
                if len(candidatos) > 1:
                    self.output_text.insert(
                        tk.END,
                        f"Nota: el serial no es unico -- {len(candidatos)} opciones "
                        f"posibles solo para el primer caracter.\n")
            else:
                self.output_text.insert(tk.END, f"Generando {count} claves validas...\n\n")
                for i, pw in enumerate(find_all_passwords(target, step, charset, limit=count), start=1):
                    self.output_text.insert(tk.END, f"[{i:>2}] {pw}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_copy(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            return
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Copiado", "Resultado copiado al portapapeles.")


if __name__ == "__main__":
    app = KeygenApp()
    app.mainloop()
