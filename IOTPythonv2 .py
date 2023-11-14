import tkinter as tk
import sqlite3
import os.path
import requests
import threading
import webbrowser
from tkinter import PhotoImage

def iniciar_flask():
    os.system("python api.py")

def abrir_navegador():
    webbrowser.open("https://www.google.com.br/maps/place/ESTACIO+DE+SA/@-19.8163046,-43.9583666,17z/data=!4m6!3m5!1s0xa68fb7bff98c97:0x981fa9f94b6616fe!8m2!3d-19.8163097!4d-43.9557917!16s%2Fg%2F11f4lk3n69?entry=ttu")

# Função para criar o banco de dados
nomeBanco = "inventario.db"
def criar_banco():
    conn = sqlite3.connect(nomeBanco)
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
            numero_serie_tag TEXT,  -- Novo campo para o número de série da TAG
            latitude REAL,
            longitude REAL,
            setor_id INTEGER,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id),
            FOREIGN KEY (setor_id) REFERENCES setores(id)
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
    cursor.execute(f"INSERT INTO {table} VALUES (NULL, {placeholders})", values)
    conn.commit()
    conn.close()

# Função para gerar relatório
def gerar_relatorio(table, field, where_clause):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    if(where_clause != None and where_clause != ''):
        cursor.execute(f"SELECT * FROM {table} WHERE {field}=?", (where_clause,))
    else:
        cursor.execute(f"SELECT * FROM {table}")
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
        result_label_login.config(text="Login bem-sucedido.")

        # Botões para adicionar registros e gerar relatórios
        adicionar_buttons = [
            ("empresas", ["Nome Empresa", "CNPJ Empresa", "Endereço Empresa"]),
            ("equipamentos", ["Empresa ID", "Modelo", "Número de Série", "Número de Série da TAG", "Latitude", "Longitude", "Setor ID"]),
            ("setores", ["Empresa ID", "Nome Setor", "Sala", "Filial/Matriz"]),
        ]

        for table, fields in adicionar_buttons:
            tk.Button(menu_frame, text=f"Adicionar {table.capitalize()}", command=lambda table=table, fields=fields: criar_janela_adicionar_registro(table, fields)).pack()

        gerar_buttons = [
            ("empresas", "nome"),
            ("equipamentos", "empresa_id"),
            ("setores", "empresa_id"),
        ]

        for table, field in gerar_buttons:
            tk.Button(menu_frame, text=f"Gerar Relatório de {table.capitalize()}", command=lambda table=table, field=field: criar_janela_gerar_relatorio(table, field)).pack()

        # Adicionando botão para rastrear TAG
        tk.Button(menu_frame, text="Rastrear TAG", command=rastrear_equipamento).pack()

        # Adicionando botão para iniciar o servidor Flask
        tk.Button(menu_frame, text="Iniciar Flask", command=lambda: threading.Thread(target=iniciar_flask).start()).pack()

        # Adicionando botão para abrir o navegador na API Flask
        tk.Button(menu_frame, text="Abrir Navegador (API)", command=abrir_navegador).pack()

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
def criar_janela_gerar_relatorio(table, field):
    def gerar():
        where_clause = entry_id.get()
        result = gerar_relatorio(table, field, where_clause)
        if not result:
            result_label.config(text=f"Nenhum registro encontrado em {table.capitalize()}.")
        else:
            result_label.config(text=f"Registros em {table.capitalize()}:")
            for r in result:
                result_label.config(text=result_label.cget("text") + f"\n{r}")

    relatorio_window = tk.Toplevel(root)
    relatorio_window.title(f"Gerar Relatório de {table.capitalize()}")

    tk.Label(relatorio_window, text=f"{field.capitalize()} do {table}").pack()
    entry_id = tk.Entry(relatorio_window)
    entry_id.pack()

    result_label = tk.Label(relatorio_window, text="", anchor='w')
    result_label.pack()

    gerar_button = tk.Button(relatorio_window, text="Gerar Relatório", command=gerar)
    gerar_button.pack()

# Função para rastrear a TAG usando o aplicativo
def rastrear_tag(numero_serie):
    # Substitua esta função com a lógica real para rastrear a TAG usando o aplicativo
    # Certifique-se de entender a API ou protocolo de comunicação fornecido pelo aplicativo da TAG
    # e faça as requisições necessárias para obter a localização da TAG com base no número de série.

    # Exemplo fictício
    url = f"https://exemplo.com/api/rastreamento?numero_serie={numero_serie}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()  # Supondo que a resposta seja um JSON contendo latitude e longitude
    else:
        return None

# Função para rastrear a TAG e exibir a localização no programa
def rastrear_equipamento():
    numero_serie = entry_numero_serie.get()
    localizacao = rastrear_tag(numero_serie)

    if localizacao:
        result_label_rastreamento.config(text=f"Localização da TAG ({numero_serie}): {localizacao['latitude']}, {localizacao['longitude']}")

        # Atualizar o banco de dados com a nova localização
        conn = sqlite3.connect('inventario.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE equipamentos SET latitude=?, longitude=? WHERE numero_serie=?", (localizacao['latitude'], localizacao['longitude'], numero_serie))
        conn.commit()
        conn.close()
    else:
        result_label_rastreamento.config(text=f"Não foi possível rastrear a TAG ({numero_serie}). Verifique o número de série.")

# Criação da janela principal
root = tk.Tk()
root.title("Sistema de Inventário")
root.geometry("600x480")

# Centralizando a logo
logo_image = PhotoImage(file="C:/Users/bruno.castro/Documents/Inventario novo/imagem.png")
logo_label = tk.Label(root, image=logo_image)
logo_label.pack(pady=20)  # Ajuste o valor de pady conforme necessário

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

# Criação do banco de dados e do usuário admin
if not os.path.isfile(nomeBanco):
    criar_banco()
    criar_usuario_admin()

# Rastreamento de Equipamentos
rastreamento_frame = tk.Frame(root)
rastreamento_frame.pack()

tk.Label(rastreamento_frame, text="Número de Série da TAG").grid(row=0, column=0)
entry_numero_serie = tk.Entry(rastreamento_frame)
entry_numero_serie.grid(row=0, column=1)

result_label_rastreamento = tk.Label(rastreamento_frame, text="")
result_label_rastreamento.grid(row=1, columnspan=2)

root.mainloop()
