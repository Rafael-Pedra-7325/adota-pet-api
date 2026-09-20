import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database
import app as app_module


class AdotaPetApiTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        database.DB_PATH = self.db_path
        database.init_db(self.db_path, seed=True)

        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

        resposta = self.client.post("/auth/login", json={"usuario": "admin", "senha": "admin123"})
        self.token = resposta.get_json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_listar_pets_publico(self):
        resposta = self.client.get("/pets")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.get_json()), 3)

    def test_filtrar_pets_por_status(self):
        resposta = self.client.get("/pets?status=disponivel")
        self.assertEqual(len(resposta.get_json()), 3)

    def test_cadastrar_pet_sem_token_falha(self):
        resposta = self.client.post("/pets", json={"nome": "Rex", "especie": "cachorro", "porte": "medio"})
        self.assertEqual(resposta.status_code, 401)

    def test_cadastrar_pet_com_token(self):
        resposta = self.client.post(
            "/pets",
            json={"nome": "Nina", "especie": "gato", "porte": "pequeno", "idade_meses": 5},
            headers=self.headers,
        )
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(len(self.client.get("/pets").get_json()), 4)

    def test_cadastrar_pet_com_porte_invalido_falha(self):
        resposta = self.client.post(
            "/pets",
            json={"nome": "X", "especie": "cachorro", "porte": "gigante"},
            headers=self.headers,
        )
        self.assertEqual(resposta.status_code, 400)

    def test_fluxo_completo_de_adocao(self):
        pet = self.client.get("/pets").get_json()[0]

        resposta = self.client.post(
            f"/pets/{pet['id']}/adotar", json={"adotante": "Rafael"}, headers=self.headers
        )
        self.assertEqual(resposta.status_code, 200)

        pet_atualizado = self.client.get(f"/pets/{pet['id']}").get_json()
        self.assertEqual(pet_atualizado["status"], "adotado")
        self.assertEqual(pet_atualizado["adotante"], "Rafael")

        resposta_duplicada = self.client.post(
            f"/pets/{pet['id']}/adotar", json={"adotante": "Outra pessoa"}, headers=self.headers
        )
        self.assertEqual(resposta_duplicada.status_code, 409)

        disponiveis = self.client.get("/pets?status=disponivel").get_json()
        self.assertEqual(len(disponiveis), 2)

    def test_remover_pet(self):
        pet = self.client.get("/pets").get_json()[0]

        resposta = self.client.delete(f"/pets/{pet['id']}", headers=self.headers)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(self.client.get("/pets").get_json()), 2)


if __name__ == "__main__":
    unittest.main()
