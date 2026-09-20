import os
import datetime
from functools import wraps

import jwt
from flask import request, jsonify

SECRET_KEY = os.environ.get("PET_SECRET_KEY", "chave-de-demonstracao-troque-em-producao")
ADMIN_USER = os.environ.get("PET_ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("PET_ADMIN_PASS", "admin123")
ALGORITHM = "HS256"


def gerar_token(usuario):
    payload = {
        "sub": usuario,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=4),
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def validar_credenciais(usuario, senha):
    return usuario == ADMIN_USER and senha == ADMIN_PASS


def token_obrigatorio(funcao):
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"erro": "Token de autenticação ausente."}), 401

        token = auth_header.split(" ", 1)[1]

        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido."}), 401

        return funcao(*args, **kwargs)

    return wrapper
