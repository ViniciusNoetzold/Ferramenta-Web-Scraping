# WebArchiver Pro • Mezzold Studio

> Ferramenta profissional de Web Scraping, extração estruturada de dados e análise de conteúdo desenvolvida pela **[Mezzold Studio](https://mezzoldstudio.com.br/)**.

[![Mezzold Studio](https://img.shields.io/badge/Powered%20by-Mezzold%20Studio-orange.svg)](https://mezzoldstudio.com.br/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)

---

## 🌐 Sobre o Projeto

O **WebArchiver Pro** é uma solução completa para arquivamento e extração de páginas web com renderização JavaScript completa via Playwright, suporte a crawler profundo com controle de taxa e exportação consolidada em pacotes `.ZIP`.

### 📦 Principais Funcionalidades
- **Renderização Dinâmica**: Scraping completo com execução de JavaScript e espera por renderização de elementos via Playwright.
- **Crawler Inteligente**: Varredura recursiva de links internos com limite de profundidade e controle de concorrência.
- **Comparação de Versões**: Análise visual e textual de mudanças entre diferentes capturas de uma mesma URL.
- **Exportação Consolidada**: Download em arquivo `.ZIP` contendo relatórios em Markdown, HTML limpo, banco de dados JSON e galeria de imagens capturadas.
- **Interface Moderna**: Dashboard com tema escuro profissional desenvolvido em Next.js e Tailwind CSS com a identidade visual da Mezzold Studio.

---

## 🚀 Deploy no Render.com

O projeto está totalmente configurado para deploy automático como Web Service no [Render.com](https://render.com/):

- **Build Command**: `./build.sh`
- **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- **Environment**: Python 3.11.8

### Arquivos de Configuração Inclusos
- `requirements.txt`: Dependências Python na raiz do repositório.
- `.python-version`: Versão 3.11.8 fixada para o runtime do Render.
- `render.yaml`: Blueprint de infraestrutura como código (IaC).
- `Procfile`: Declaração de processo web para compatibilidade com PaaS.
- `build.sh`: Script de automação de build e instalação dos binários do Playwright.

---

## 💻 Execução Local

### Pré-requisitos
- Python 3.11+
- Node.js 18+ (apenas se desejar recompilar o frontend)

### Iniciar o Servidor Integrado (Backend + Frontend)
```bash
pip install -r requirements.txt
playwright install chromium
python run.py
```
Acesse no navegador: **http://localhost:8000**

---

## 🏢 Mezzold Studio
- **Website Oficial**: [mezzoldstudio.com.br](https://mezzoldstudio.com.br/)
- **Especialidade**: Software House Premium • Micro SaaS & Dashboards de Alta Performance
