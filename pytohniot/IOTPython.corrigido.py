import tkinter as tk
import sqlite3
# from PIL import Image, ImageTk

# Função para criar o banco de dados
def criar_banco():
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cnpj TEXT,
            endereco TEXT
        );

        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER,
            modelo TEXT,
            numero_serie TEXT,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        );

        CREATE TABLE IF NOT EXISTS setores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER,
            nome_setor TEXT,
            sala TEXT,
            filial_matriz TEXT,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        );

        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        );
    ''')
    conn.commit()
    conn.close()

# Função para criar o usuário admin
def criar_usuario_admin():
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)", ('admin', '123'))
    conn.commit()
    conn.close()

# Funções para adicionar registros
def adicionar_registro(table, *values):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    placeholders = ', '.join(['?'] * len(values))
    print(table)
    print(placeholders)
    cursor.execute(f"INSERT INTO {table} VALUES (NULL,{placeholders})", values)
    conn.commit()
    conn.close()

# Função para gerar relatório
def gerar_relatorio(table, where_clause):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE {where_clause}")
    result = cursor.fetchall()
    conn.close()
    return result

# Função para fazer login
def fazer_login():
    username = entry_username.get()
    password = entry_password.get()

    if username == 'admin' and password == '123':
        entry_username.config(state='disabled')
        entry_password.config(state='disabled')
        login_button.config(state='disabled')
        #menu_button.config(state='normal')
        result_label_login.config(text="Login bem-sucedido.")

                # Botões para adicionar registros e gerar relatórios
        adicionar_buttons = [
            ("empresas", ["Nome Empresa", "CNPJ Empresa", "Endereço Empresa"]),
            ("equipamentos", ["Empresa ID", "Modelo", "Número de Série"]),
            ("setores", ["Empresa ID", "Nome Setor", "Sala", "Filial/Matriz"]),
        ]

        for table, fields in adicionar_buttons:
            tk.Button(menu_frame, text=f"Adicionar {table.capitalize()}", command=lambda table=table, fields=fields: criar_janela_adicionar_registro(table, fields)).pack()

        gerar_buttons = [
            ("empresa", "nome"),
            ("equipamento", "empresa_id"),
            ("setor", "empresa_id"),
        ]

        for table, field in gerar_buttons:
            tk.Button(menu_frame, text=f"Gerar Relatório de {table.capitalize()}", command=lambda table=table, field=field: criar_janela_gerar_relatorio(table, [field])).pack()

    else:
        result_label_login.config(text="Login falhou. Verifique seu nome de usuário e senha.")

# Função para criar uma nova janela para adicionar um registro
def criar_janela_adicionar_registro(table, fields):
    def adicionar():
        values = [entry.get() for entry in entries]
        adicionar_registro(table, *values)
        result_label.config(text=f"{table.capitalize()} cadastrado com sucesso.")
        for entry in entries:
            entry.delete(0, tk.END)

    adicionar_window = tk.Toplevel(root)
    adicionar_window.title(f"Adicionar {table.capitalize()}")

    entries = [tk.Entry(adicionar_window) for _ in fields]

    for i, (label, entry) in enumerate(zip(fields, entries)):
        tk.Label(adicionar_window, text=label).grid(row=i, column=0)
        entry.grid(row=i, column=1)

    result_label = tk.Label(adicionar_window, text="")
    result_label.grid(row=len(fields), columnspan=2)

    adicionar_button = tk.Button(adicionar_window, text="Adicionar", command=adicionar)
    adicionar_button.grid(row=len(fields) + 1, columnspan=2)

# Função para criar uma nova janela para gerar relatórios
def criar_janela_gerar_relatorio(table, fields):
    def gerar():
        where_clause = entry_id.get()
        result = gerar_relatorio(table, where_clause)
        if not result:
            result_label.config(text=f"Nenhum registro encontrado em {table.capitalize()}.")
        else:
            result_label.config(text=f"Registros em {table.capitalize()}:")
            for r in result:
                result_label.config(text=result_label.cget("text") + f"\n{r}")

    relatorio_window = tk.Toplevel(root)
    relatorio_window.title(f"Gerar Relatório de {table.capitalize()}")

    tk.Label(relatorio_window, text=f"ID do {table}").pack()
    entry_id = tk.Entry(relatorio_window)
    entry_id.pack()

    result_label = tk.Label(relatorio_window, text="")
    result_label.pack()

    gerar_button = tk.Button(relatorio_window, text="Gerar Relatório", command=gerar)
    gerar_button.pack()

# Função para carregar a imagem de fundo
# def carregar_imagem_de_fundo():
#     try:
#         image = Image.open('C:/imagem/imagem1.jpg')
#         photo = ImageTk.PhotoImage(image)
#         img_label = tk.Label(root, image=photo)
#         img_label.photo = photo
#         img_label.place(x=0, y=0, relwidth=1, relheight=1)
#     except Exception as e:
#         print(f"Erro ao carregar a imagem: {e}")

# Criação da janela principal
root = tk.Tk()
root.title("Sistema de Inventário")

# Carregar imagem de fundo
# carregar_imagem_de_fundo()

# Menu de Login
login_frame = tk.Frame(root)
login_frame.pack()

entry_username = tk.Entry(login_frame)
entry_password = tk.Entry(login_frame, show='*')
result_label_login = tk.Label(login_frame, text="")

entry_username.grid(row=0, column=1)
entry_password.grid(row=1, column=1)
result_label_login.grid(row=2, columnspan=2)

login_button = tk.Button(login_frame, text="Login", command=fazer_login)
login_button.grid(row=3, columnspan=2)

# Menu Principal
menu_frame = tk.Frame(root)
menu_frame.pack()
# menu_button = tk.Button(menu_frame, text="Menu Principal", state='disabled')
# menu_button.pack()

# Criação do banco de dados e do usuário admin
criar_banco()
criar_usuario_admin()

root.mainloop()
