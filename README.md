# Digital Soluctions - Chat Automatizado com IA

Sistema profissional de chat automatizado com captura de leads e integração com IA Gemini.

## 🎯 Funcionalidades

- ✅ Captura de leads (nome + telefone)
- ✅ Identificação automática de nicho via parâmetro `?tag=`
- ✅ Chat inteligente com IA Gemini
- ✅ Interface responsiva e moderna (Tailwind CSS)
- ✅ Design premium estilo WhatsApp
- ✅ Salvamento em banco SQLite
- ✅ Redirecionamento personalizado por nicho
- ✅ Animações suaves e scroll automático

## 📁 Estrutura do Projeto

```
.
├── app.py                  # Aplicação Flask principal
├── main.py                 # Ponto de entrada
├── db_init.py              # Inicialização do banco de dados
├── gemini.py               # Integração com IA Gemini
├── leads.db                # Banco de dados SQLite (criado automaticamente)
├── static/
│   ├── css/
│   │   └── style.css       # Estilos personalizados
│   └── js/
│       └── chat.js         # Lógica do chat (AJAX)
├── templates/
│   ├── base.html           # Template base
│   ├── chat.html           # Interface do chat
│   └── thankyou.html       # Página de agradecimento
└── README.md
```

## 🚀 Como Rodar no Replit

1. **Configure as variáveis de ambiente obrigatórias:**
   - `GEMINI_API_KEY`: Sua chave da API do Gemini (obtenha em: https://aistudio.google.com/app/apikey)
   - `SESSION_SECRET`: Chave secreta para sessões (gere uma aleatória forte)
   
   **IMPORTANTE:** O sistema não iniciará sem essas variáveis configuradas por razões de segurança.

2. **Execute o projeto:**
   - Clique no botão "Run" no Replit
   - O servidor Flask iniciará automaticamente na porta 5000

3. **Acesse o chat:**
   - URL base: `https://seu-projeto.replit.dev/`
   - Com tag personalizada: `https://seu-projeto.replit.dev/?tag=marketing`

## 🏷️ Tags de Nicho

Configure diferentes nichos adicionando o parâmetro `?tag=` na URL:

- `?tag=marketing` → Redireciona para página de marketing
- `?tag=tecnologia` → Redireciona para página de tecnologia
- `?tag=vendas` → Redireciona para página de vendas
- `?tag=consultoria` → Redireciona para página de consultoria

### Como Adicionar Novas Tags

Edite o dicionário `NICHO_URLS` no arquivo `app.py`:

```python
NICHO_URLS = {
    "marketing": "https://example.com/marketing",
    "tecnologia": "https://example.com/tecnologia",
    "seu_nicho": "https://seu-site.com/pagina",
    "default": "https://digitalsoluctions.com"
}
```

## 💾 Banco de Dados

O sistema usa SQLite puro (sem ORM) com a seguinte estrutura:

**Tabela `leads`:**
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT)
- `phone` (TEXT)
- `tag` (TEXT)
- `created_at` (TIMESTAMP)

**IMPORTANTE:** O arquivo `leads.db` é criado automaticamente na primeira execução e está incluído no `.gitignore` para proteger os dados dos leads. Nunca faça commit deste arquivo no controle de versão.

### Visualizar Leads Cadastrados

Execute no terminal:

```bash
python3 -c "from db_init import get_all_leads; print(get_all_leads())"
```

## 🎨 Personalização

### Cores
Edite as cores no arquivo `templates/base.html` e `static/css/style.css`:
- Azul principal: `#2563eb` (bg-blue-600)
- Branco: `#FFFFFF`
- Cinza: tons de gray (50, 100, 200, etc.)

### Nome da Empresa
Altere "Digital Soluctions" em `templates/base.html` (linha do header).

## 🔧 Tecnologias Utilizadas

- **Backend:** Python 3.11 + Flask
- **Frontend:** HTML5 + Tailwind CSS + JavaScript
- **Banco de Dados:** SQLite3
- **IA:** Google Gemini API (gemini-2.5-flash)
- **Deploy:** Gunicorn (pronto para produção)

## 📱 Responsividade

O sistema é mobile-first e totalmente responsivo:
- Funciona perfeitamente em smartphones
- Interface adaptada para tablets
- Design fluido para desktop

## 🌐 Deploy no Render

Para hospedar no Render:

1. **Faça o deploy no Render:**
   - Conecte seu repositório Git ao Render
   - Configure o build command: `pip install -r requirements.txt`
   - Configure o start command: `gunicorn --bind 0.0.0.0:$PORT main:app`

2. **Configure as variáveis de ambiente (OBRIGATÓRIO):**
   - `GEMINI_API_KEY`: Sua chave da API do Gemini
   - `SESSION_SECRET`: Chave secreta forte para sessões (use um gerador de senhas)
   
   **IMPORTANTE:** O sistema não iniciará sem essas variáveis configuradas por razões de segurança.

3. **Banco de dados:**
   - Para produção, considere migrar de SQLite para PostgreSQL
   - Render oferece PostgreSQL gratuito para pequenos projetos

## 📄 Dependências

```
Flask
google-genai
python-dotenv
gunicorn
```

## 🤝 Fluxo do Chat

1. Usuário acessa o chat (opcionalmente com `?tag=nicho`)
2. Sistema pergunta o nome
3. Sistema pergunta o telefone
4. Dados são salvos no banco SQLite
5. Chat com IA é ativado (Gemini responde perguntas)
6. Usuário digita "finalizar" para encerrar
7. Redirecionamento para página personalizada do nicho

## 📞 Suporte

Sistema desenvolvido para Digital Soluctions.

Para dúvidas sobre a API do Gemini: https://ai.google.dev/gemini-api/docs
