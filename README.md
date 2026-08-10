# WebArchiver Pro

Uma ferramenta profissional para arquivamento e extração de dados de websites.

## 🚀 Como instalar e rodar em outro PC

Para rodar este projeto em outro computador, você precisará ter instalado:
1. **Node.js** (versão 18+ recomendada) - [Baixar Node.js](https://nodejs.org/)
2. **Python** (versão 3.11+ recomendada) - [Baixar Python](https://www.python.org/)

### Passos para inicialização

1. **Clone ou baixe** este repositório para o novo computador.

2. **Configuração do Backend (Python)**
   Abra um terminal na pasta `backend`:
   ```bash
   cd backend
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Mac/Linux:
   # source venv/bin/activate
   
   pip install -r requirements.txt
   playwright install
   ```

3. **Configuração do Frontend (Node.js)**
   Abra outro terminal na pasta `frontend`:
   ```bash
   cd frontend
   npm install
   ```

4. **Variáveis de Ambiente (API Keys)**
   Certifique-se de que o arquivo `.env` está presente na pasta `backend`. Ele contém as chaves de API necessárias (NVIDIA, GROK, etc). *(Nota: Cuidado ao compartilhar o arquivo .env publicamente!)*

### Rodando o Projeto

Você precisa iniciar o backend e o frontend simultaneamente (em terminais separados).

**Iniciar o Backend:**
```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

**Iniciar o Frontend:**
```bash
cd frontend
npm run dev
```

Após iniciar ambos, acesse o aplicativo em seu navegador no endereço: **http://localhost:3000**

## 📦 Funcionalidades
- Extração de sites com renderização JS (Playwright)
- Crawler inteligente com suporte a profundidade máxima
- Comparação de diferentes versões de páginas
- Exportação de todo o conteúdo (textos, imagens, posições, HTML) em um único pacote `.ZIP`
- Histórico de todas as análises realizadas
