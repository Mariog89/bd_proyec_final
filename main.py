from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/procesar", methods=["POST"])
def procesar():
    dato = request.form["mi_dato"]
    resultado = f"Hola, {dato}!"
    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)
