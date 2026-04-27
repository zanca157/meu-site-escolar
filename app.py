from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "segredo"

def conectar():
    return sqlite3.connect("escola.db")

def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        senha TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        materia TEXT,
        n1 REAL, n2 REAL, n3 REAL, n4 REAL
    )
    """)

    conn.commit()
    conn.close()

criar_banco()

materias = [
    "Matemática","Ciências Modelada","Biologia","Química","Física",
    "Redação Nota 1000","Artes","Educação Física","Escritura Autoral",
    "Filosofia","História","Inglês","Literatura","Sociologia",
    "Urbanismo","Geografia","Gramática","Projeto de Vida","Produção Textual"
]

def calcular_media(notas):
    notas_validas = [n for n in notas if n > 0]
    if not notas_validas:
        return 0
    return sum(notas_validas) / len(notas_validas)

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form["user"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE username=? AND senha=?", (user, senha))
        if cursor.fetchone():
            session["user"] = user
            return redirect("/boletim")

        return "Login inválido"

    return render_template("login.html")

@app.route("/registro", methods=["GET","POST"])
def registro():
    if request.method == "POST":
        user = request.form["user"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO usuarios (username, senha) VALUES (?,?)", (user, senha))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("registro.html")

@app.route("/boletim", methods=["GET","POST"])
def boletim():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        for materia in materias:
            notas = []
            for i in range(1,5):
                valor = request.form.get(f"{materia}_{i}")
                nota = float(valor) if valor else 0
                notas.append(nota)

            cursor.execute("DELETE FROM notas WHERE usuario=? AND materia=?", (session["user"], materia))

            cursor.execute("""
                INSERT INTO notas (usuario, materia, n1,n2,n3,n4)
                VALUES (?,?,?,?,?,?)
            """, (session["user"], materia, *notas))

        conn.commit()

    dados = {}
    medias = {}
    soma = 0

    for materia in materias:
        cursor.execute("SELECT n1,n2,n3,n4 FROM notas WHERE usuario=? AND materia=?", (session["user"], materia))
        res = cursor.fetchone()
        notas = list(res) if res else [0,0,0,0]

        media = calcular_media(notas)
        dados[materia] = notas
        medias[materia] = media
        soma += media

    media_geral = soma / len(materias)
    status = "Aprovado" if media_geral >= 6 else "Reprovado"

    conn.close()

    return render_template("boletim.html",
                           dados=dados,
                           medias=medias,
                           media_geral=media_geral,
                           status=status)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)