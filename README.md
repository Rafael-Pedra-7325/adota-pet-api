# 🐾 AdotaPet API

API REST para gestão de pets disponíveis para adoção, com autenticação JWT, testes automatizados e **integração contínua via GitHub Actions**.

## ✨ Funcionalidades
- Listagem pública de pets (com filtro por status: `disponivel` / `adotado`)
- Cadastro, atualização e remoção de pets (rotas protegidas)
- Registro de adoção, com validação para não adotar duas vezes o mesmo pet
- 7 testes automatizados cobrindo o fluxo completo, incluindo casos de erro
- Workflow de CI que roda os testes a cada push/PR

## 🏗️ Arquitetura
```
adota-pet-api/
├── app.py
├── database.py
├── auth.py
├── tests/
│   └── test_api.py
├── .github/
│   └── workflows/
│       └── tests.yml     # CI: roda os testes automaticamente
└── requirements.txt
```

## 🚀 Como executar
```bash
pip install -r requirements.txt
python app.py
```
API em `http://localhost:5005`, com 3 pets de exemplo já cadastrados.

## 🔐 Autenticação
```bash
curl -X POST http://localhost:5005/auth/login \
  -H "Content-Type: application/json" \
  -d '{"usuario": "admin", "senha": "admin123"}'
```

## 📖 Principais endpoints

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| GET | `/pets` | não | Lista pets (filtro `?status=`) |
| GET | `/pets/<id>` | não | Detalhe de um pet |
| POST | `/pets` | sim | Cadastra um pet |
| PUT | `/pets/<id>` | sim | Atualiza um pet |
| POST | `/pets/<id>/adotar` | sim | Registra a adoção |
| DELETE | `/pets/<id>` | sim | Remove um pet |

## 🧪 Testes
```bash
python -m unittest tests.test_api -v
```

## ⚙️ CI/CD
O workflow em `.github/workflows/tests.yml` roda automaticamente a suíte de testes a cada `push` e `pull request` na branch `main` — é esse workflow que gera o badge de "build passing" no topo do repositório (veja o passo a passo no guia de criação de repositório).

## 🔭 Próximos passos
- Upload de foto do pet (com armazenamento em disco ou S3)
- Paginação e busca por espécie/porte
- Deploy automático após os testes passarem (CD)
