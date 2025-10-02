# 🍽️ MS Cardápios Diários
Microserviço responsável por gerenciar **cardápios diários** em diferentes turnos do dia (manhã, tarde e noite).  
Ele permite criar, atualizar, listar e consultar cardápios, garantindo que não haja duplicidade por **data + turno**.  
Além disso, todos os itens (pratos, acompanhamentos, saladas, sobremesas e bebidas) são **validados via MS-Estoque** antes de serem persistidos.  

---

## 🚀 Tecnologias Utilizadas
- **Python 3.12** com **FastAPI**
- **SQLAlchemy ORM** (PostgreSQL no Render)
- **Pydantic v2** (validação de dados)
- **Requests** (integração com MS-Estoque)
- **JWT** (validação de autenticação via serviço externo)
- **Render** (deploy em nuvem)
- **DBeaver** (administração e consultas no banco)

---

## 📂 Estrutura do Projeto
- ├── main.py # Ponto de entrada da aplicação
- ├── db/
- │ └── database.py # Configuração do banco
- ├── routers/
- │ └── cardapio_router.py # Rotas da API
- ├── models/
- │ └── cardapio_model.py # Modelo ORM
- ├── schemas/
- │ └── cardapio_schema.py # Schemas Pydantic
- ├── services/
- │ └── estoque_service.py # Validação de IDs via MS-Estoque
- ├── middlewares/
- │ └── auth_middleware.py # Middleware JWT
- ├── configs/
- │ └── cors_config.py # Configuração de CORS
---

## ⚙️ Configuração do Ambiente

### 1. Clonar o repositório
```bash
git clone https://github.com/CodeWave-Innovations-Group-CWI-Group/ms-cardapio.git
cd ms-cardapio
```
---
### 2. Criar ambiente virtual e instalar dependências
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt

```
### 3. Configurar variáveis de ambiente
Crie um arquivo .env na raiz do projeto:
```bash
DATABASE_URL="postgresql://usuario:senha@host:5432/ms_cardapio_db"
ESTOQUE_API_BASE="https://ms-estoque.onrender.com/api/v1/itens"
AUTH_API_BASE=""

```
### 4. Executar localmente
```bash
uvicorn main:app --reload

```
### 5. Acessar a documentação
```
Swagger UI → http://localhost:8000/docs

```
## 🗄️ Banco de Dados
```commandline
class Cardapio(Base):
    __tablename__ = "cardapios"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False, index=True)
    turno = Column(Enum(TurnoEnum, name="turno_enum"), nullable=False)
    prato_principal_ids = Column(ARRAY(Integer), nullable=False)
    acompanhamento_ids  = Column(ARRAY(Integer), nullable=False)
    salada_ids          = Column(ARRAY(Integer), nullable=False)
    sobremesa_ids       = Column(ARRAY(Integer), nullable=False)
    bebida_ids          = Column(ARRAY(Integer), nullable=False)

    __table_args__ = (UniqueConstraint("data", "turno", name="unique_data_turno"),)

```
#### 🔒 Cada cardápio é único por data + turno.

## 🔑 Autenticação
- Todas as rotas (exceto /health) exigem token JWT.
- O middleware **auth_middleware.py** valida o token em uma API externa:

- GET /api/v1/auth/validate-token/

- GET /api/v1/profile/me/

- Se válido, o usuário é anexado em request.state.user.

## 📌 Funcionalidades
- Criar cardápio (valida itens no MS-Estoque)
- Atualizar cardápio (PUT/PATCH)
- Listar cardápios (todos, por data, por turno)
- Consultar cardápio por ID
- Remover cardápio

---

## 🔑 Endpoints principais

### ➕ Criar Cardápio
```http
POST /api/v1/cardapios/
```
### 📜 Listar Cardápios de Hoje
```http
GET /api/v1/cardapios/hoje?turno=MANHA

```
### ✏️ Atualizar Cardápio
```http
PUT /api/v1/cardapios/{id}
PATCH /api/v1/cardapios/{id}

```
### 🔍 Consultar por ID
```http
GET /api/v1/cardapios/{id}

```
### ❌ Remover Cardápio
```http
DELETE /api/v1/cardapios/{id}

```

# 🛡️ Regras de Negócio
- Cada data + turno só pode ter um cardápio.
- Todos os IDs enviados são validados no MS-Estoque.
- A autenticação é obrigatória via token JWT.