"""
AdotaPet API
API REST para gestão de pets disponíveis para adoção, com autenticação JWT
e cobertura de testes automatizados (rodando em CI via GitHub Actions).
"""

from flask import Flask, jsonify, request

from database import get_connection, init_db
from auth import gerar_token, validar_credenciais, token_obrigatorio

app = Flask(__name__)


@app.route("/")
def raiz():
    return jsonify({"servico": "AdotaPet API", "status": "online"})


@app.route("/auth/login", methods=["POST"])
def login():
    dados = request.get_json(silent=True) or {}
    usuario = dados.get("usuario", "")
    senha = dados.get("senha", "")

    if not validar_credenciais(usuario, senha):
        return jsonify({"erro": "Usuário ou senha inválidos."}), 401

    return jsonify({"token": gerar_token(usuario)})


@app.route("/pets", methods=["GET"])
def listar_pets():
    status = request.args.get("status")

    with get_connection() as conn:
        if status:
            pets = conn.execute("SELECT * FROM pets WHERE status = ?", (status,)).fetchall()
        else:
            pets = conn.execute("SELECT * FROM pets").fetchall()

    return jsonify([dict(p) for p in pets])


@app.route("/pets/<int:pet_id>", methods=["GET"])
def obter_pet(pet_id):
    with get_connection() as conn:
        pet = conn.execute("SELECT * FROM pets WHERE id = ?", (pet_id,)).fetchone()

    if pet is None:
        return jsonify({"erro": "Pet não encontrado."}), 404

    return jsonify(dict(pet))


@app.route("/pets", methods=["POST"])
@token_obrigatorio
def cadastrar_pet():
    dados = request.get_json(silent=True) or {}
    nome = dados.get("nome")
    especie = dados.get("especie")
    porte = dados.get("porte")
    idade_meses = dados.get("idade_meses")
    descricao = dados.get("descricao", "")

    if not nome or not especie or porte not in ("pequeno", "medio", "grande"):
        return jsonify({"erro": "Campos 'nome', 'especie' e 'porte' (pequeno/medio/grande) são obrigatórios."}), 400

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO pets (nome, especie, idade_meses, porte, descricao) VALUES (?, ?, ?, ?, ?)",
            (nome, especie, idade_meses, porte, descricao),
        )
        novo_id = cursor.lastrowid

    return jsonify({"id": novo_id, "nome": nome, "especie": especie, "porte": porte}), 201


@app.route("/pets/<int:pet_id>", methods=["PUT"])
@token_obrigatorio
def atualizar_pet(pet_id):
    dados = request.get_json(silent=True) or {}

    with get_connection() as conn:
        pet = conn.execute("SELECT * FROM pets WHERE id = ?", (pet_id,)).fetchone()
        if pet is None:
            return jsonify({"erro": "Pet não encontrado."}), 404

        nome = dados.get("nome", pet["nome"])
        descricao = dados.get("descricao", pet["descricao"])
        idade_meses = dados.get("idade_meses", pet["idade_meses"])

        conn.execute(
            "UPDATE pets SET nome = ?, descricao = ?, idade_meses = ? WHERE id = ?",
            (nome, descricao, idade_meses, pet_id),
        )

    return jsonify({"mensagem": "Pet atualizado com sucesso."})


@app.route("/pets/<int:pet_id>/adotar", methods=["POST"])
@token_obrigatorio
def adotar_pet(pet_id):
    dados = request.get_json(silent=True) or {}
    adotante = dados.get("adotante")

    if not adotante:
        return jsonify({"erro": "Informe o nome do adotante em 'adotante'."}), 400

    with get_connection() as conn:
        pet = conn.execute("SELECT * FROM pets WHERE id = ?", (pet_id,)).fetchone()

        if pet is None:
            return jsonify({"erro": "Pet não encontrado."}), 404
        if pet["status"] == "adotado":
            return jsonify({"erro": "Este pet já foi adotado."}), 409

        conn.execute(
            "UPDATE pets SET status = 'adotado', adotante = ? WHERE id = ?",
            (adotante, pet_id),
        )

    return jsonify({"mensagem": f"{pet['nome']} foi adotado(a) por {adotante}!"})


@app.route("/pets/<int:pet_id>", methods=["DELETE"])
@token_obrigatorio
def remover_pet(pet_id):
    with get_connection() as conn:
        pet = conn.execute("SELECT * FROM pets WHERE id = ?", (pet_id,)).fetchone()
        if pet is None:
            return jsonify({"erro": "Pet não encontrado."}), 404
        conn.execute("DELETE FROM pets WHERE id = ?", (pet_id,))

    return jsonify({"mensagem": "Pet removido."})


if __name__ == "__main__":
    init_db(seed=True)
    app.run(debug=True, port=5005)
