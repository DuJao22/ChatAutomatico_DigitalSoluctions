import os
import re
import sys
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from db_init import init_db, save_lead
from gemini import ask_gemini, extract_user_info, get_product_link

if not os.environ.get("SESSION_SECRET"):
    print("ERROR: SESSION_SECRET environment variable is not set!", file=sys.stderr)
    sys.exit(1)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

init_db()

NICHO_URLS = {
    # Nichos principais
    "marketing": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=marketing",
    "tecnologia": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=tecnologia",
    "vendas": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=vendas",
    "consultoria": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=consultoria",
    "ecommerce": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=ecommerce",
    "startup": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=startup",
    
    # Produtos específicos
    "barbearia": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=barbearia",
    "restaurante": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=restaurante",
    "meatz": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=meatz",
    "hamburgueria": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=hamburgueria",
    "lanchonete": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=lanchonete",
    
    # Serviços de desenvolvimento
    "sites": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=sites",
    "site_profissional": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=site_profissional",
    "landing_page": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=landing_page",
    "sistema": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=sistema",
    "app": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=app",
    
    # Serviços de design
    "identidade_visual": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=identidade_visual",
    "design": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=design",
    "logo": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=logo",
    "branding": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=branding",
    
    # Serviços de tecnologia
    "automacao": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=automacao",
    "chatbot": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=chatbot",
    "ia": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=ia",
    
    # Serviços de marketing
    "trafego_pago": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=trafego_pago",
    "social_media": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=social_media",
    "instagram": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=instagram",
    "facebook_ads": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=facebook_ads",
    "google_ads": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=google_ads",
    
    # Páginas gerais
    "portfolio": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=portfolio",
    "sobre": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=sobre",
    "contato": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=contato",
    "home": "https://chatautomatico-digitalsoluctions.onrender.com/?tag=home",
    
    # Default
    "default": "https://chatautomatico-digitalsoluctions.onrender.com/"
}

# Mapeamento de nichos para mensagens personalizadas
NICHO_MENSAGENS = {
    # Nichos principais
    "marketing": "marketing digital",
    "tecnologia": "soluções de tecnologia",
    "vendas": "vendas e conversão",
    "consultoria": "consultoria empresarial",
    "ecommerce": "e-commerce e vendas online",
    "startup": "soluções para startups",
    
    # Produtos específicos
    "barbearia": "soluções para barbearias",
    "restaurante": "soluções para restaurantes",
    "meatz": "soluções para hamburguerias",
    "hamburgueria": "soluções para hamburguerias",
    "lanchonete": "soluções para lanchonetes",
    
    # Serviços de desenvolvimento
    "sites": "criação de sites profissionais",
    "landing_page": "landing pages de alta conversão",
    "sistema": "sistemas personalizados",
    "app": "desenvolvimento de aplicativos",
    
    # Serviços de design
    "identidade_visual": "identidade visual",
    "design": "design profissional",
    "logo": "criação de logotipos",
    "branding": "branding e posicionamento",
    
    # Serviços de tecnologia
    "automacao": "automação de processos",
    "chatbot": "chatbots inteligentes",
    "ia": "inteligência artificial",
    
    # Serviços de marketing
    "trafego_pago": "tráfego pago",
    "social_media": "gestão de redes sociais",
    "instagram": "gestão de Instagram",
    "facebook_ads": "anúncios no Facebook",
    "google_ads": "Google Ads",
    
    # Default
    "default": "nossas soluções"
}

# Mapeamento de produtos/serviços para links das páginas
PRODUTO_LINKS = {
    # PRODUTOS COMPLETOS - Links específicos de cada produto
    "barbearia": "https://fullstackdavi.github.io/DigitalSoluctions/produto-barbearia.html",
    "meatz": "https://fullstackdavi.github.io/DigitalSoluctions/produto-meatz.html",
    "restaurante": "https://fullstackdavi.github.io/DigitalSoluctions/produto-meatz.html",
    "site_profissional": "https://fullstackdavi.github.io/DigitalSoluctions/produto.html",
    
    # SERVIÇOS - Página de serviços
    "sites": "https://fullstackdavi.github.io/DigitalSoluctions/#services",
    "landing_page": "https://fullstackdavi.github.io/DigitalSoluctions/#services",
    "identidade_visual": "https://fullstackdavi.github.io/DigitalSoluctions/#services",
    "design": "https://fullstackdavi.github.io/DigitalSoluctions/#services",
    "automacao": "https://fullstackdavi.github.io/DigitalSoluctions/#services",
    "chatbot": "https://fullstackdavi.github.io/DigitalSoluctions/#services",
    "ia": "https://fullstackdavi.github.io/DigitalSoluctions/#services",
    "trafego_pago": "https://fullstackdavi.github.io/DigitalSoluctions/#services",
    "marketing": "https://fullstackdavi.github.io/DigitalSoluctions/#services",
    "social_media": "https://fullstackdavi.github.io/DigitalSoluctions/#services",
    
    # PÁGINAS GERAIS
    "portfolio": "https://fullstackdavi.github.io/DigitalSoluctions/#products",
    "sobre": "https://fullstackdavi.github.io/DigitalSoluctions/#about",
    "contato": "https://fullstackdavi.github.io/DigitalSoluctions/#contact",
    "home": "https://fullstackdavi.github.io/DigitalSoluctions/",
}

def get_qualification_question(tag: str, question_num: int) -> str:
    """
    Retorna perguntas de qualificação específicas por nicho
    """
    questions = {
        # NICHOS ALIMENTAÇÃO
        "barbearia": {
            1: "Pergunta 1/3: Qual é o nome da sua barbearia? 💈",
            2: "Pergunta 2/3: Qual é seu principal desafio hoje? (ex: agenda desorganizada, clientes faltando, falta de controle financeiro)",
            3: "Pergunta 3/3: Você já usa redes sociais para divulgar seus cortes? Qual?"
        },
        "restaurante": {
            1: "Pergunta 1/3: Qual é o nome do seu restaurante? 🍽️",
            2: "Pergunta 2/3: Como você recebe pedidos hoje? (WhatsApp, telefone, etc.)",
            3: "Pergunta 3/3: Você tem cardápio online? Seus clientes sabem seus pratos pelas redes sociais?"
        },
        "hamburgueria": {
            1: "Pergunta 1/3: Qual é o nome da sua hamburgueria? 🍔",
            2: "Pergunta 2/3: Como você recebe pedidos hoje? (WhatsApp, telefone, etc.)",
            3: "Pergunta 3/3: Você tem cardápio online? Seus clientes sabem seus burgers pelas redes sociais?"
        },
        "meatz": {
            1: "Pergunta 1/3: Qual é o nome da sua hamburgueria/lanchonete? 🍔",
            2: "Pergunta 2/3: Como você controla seus pedidos hoje? Tem muitos erros ou pedidos perdidos?",
            3: "Pergunta 3/3: Quanto você gasta por mês com iFood/Rappi? Gostaria de ter seu próprio sistema?"
        },
        "lanchonete": {
            1: "Pergunta 1/3: Qual é o nome da sua lanchonete? 🥪",
            2: "Pergunta 2/3: Como você recebe pedidos hoje? (WhatsApp, telefone, etc.)",
            3: "Pergunta 3/3: Seus clientes conhecem seu cardápio completo? Você divulga nas redes sociais?"
        },
        
        # NICHOS E-COMMERCE E VENDAS
        "ecommerce": {
            1: "Pergunta 1/3: Qual é o nome da sua loja online? 🛒",
            2: "Pergunta 2/3: Qual é o principal problema do seu site hoje? (vendas baixas, tráfego caro, carrinhos abandonados)",
            3: "Pergunta 3/3: Você investe em tráfego pago? Google Ads, Facebook Ads?"
        },
        "vendas": {
            1: "Pergunta 1/3: Qual produto/serviço você vende? 💰",
            2: "Pergunta 2/3: Qual é seu maior obstáculo para vender mais? (leads frios, falta de presença online, concorrência)",
            3: "Pergunta 3/3: Como seus clientes te encontram hoje? Você tem site ou landing page?"
        },
        
        # NICHOS MARKETING
        "marketing": {
            1: "Pergunta 1/3: Para qual empresa/negócio você faz marketing? 📊",
            2: "Pergunta 2/3: Qual é seu maior desafio em marketing digital hoje?",
            3: "Pergunta 3/3: Você já investe em tráfego pago? Qual plataforma?"
        },
        "trafego_pago": {
            1: "Pergunta 1/3: Para qual negócio você quer tráfego pago? 🎯",
            2: "Pergunta 2/3: Você já rodou campanhas? Qual foi o maior problema? (custo alto, baixa conversão, etc.)",
            3: "Pergunta 3/3: Qual é seu orçamento mensal para anúncios?"
        },
        "social_media": {
            1: "Pergunta 1/3: Qual empresa/negócio precisa de gestão de redes sociais? 📱",
            2: "Pergunta 2/3: Quais redes sociais você usa? (Instagram, Facebook, TikTok, LinkedIn)",
            3: "Pergunta 3/3: Você posta com frequência? Sente que não engaja o suficiente?"
        },
        "instagram": {
            1: "Pergunta 1/3: Qual é o nome do seu negócio/marca no Instagram? 📸",
            2: "Pergunta 2/3: Quantos seguidores você tem hoje? Você vende pelo Instagram?",
            3: "Pergunta 3/3: Qual é seu maior desafio? (crescer, engajar, vender, criar conteúdo)"
        },
        "facebook_ads": {
            1: "Pergunta 1/3: Qual produto/serviço você quer anunciar no Facebook? 📢",
            2: "Pergunta 2/3: Você já rodou anúncios antes? Qual foi o resultado?",
            3: "Pergunta 3/3: Qual é seu objetivo principal? (vendas, leads, reconhecimento de marca)"
        },
        "google_ads": {
            1: "Pergunta 1/3: Qual produto/serviço você quer anunciar no Google? 🔍",
            2: "Pergunta 2/3: Você já usa Google Ads? Está satisfeito com os resultados?",
            3: "Pergunta 3/3: Qual é seu orçamento mensal para campanhas?"
        },
        
        # NICHOS TECNOLOGIA
        "tecnologia": {
            1: "Pergunta 1/3: Qual é o nome da sua empresa/startup? 💻",
            2: "Pergunta 2/3: Qual processo você mais precisa automatizar hoje?",
            3: "Pergunta 3/3: Você tem site profissional? Como os clientes te encontram?"
        },
        "startup": {
            1: "Pergunta 1/3: Qual é o nome da sua startup? 🚀",
            2: "Pergunta 2/3: Qual é o maior gargalo da sua startup hoje? (MVP lento, falta de clientes, produto caro)",
            3: "Pergunta 3/3: Você já tem investidores? Precisa de pitch deck ou identidade visual profissional?"
        },
        "automacao": {
            1: "Pergunta 1/3: Qual é o nome da sua empresa? 🤖",
            2: "Pergunta 2/3: Qual processo manual você mais quer automatizar? (atendimento, vendas, cadastros, etc.)",
            3: "Pergunta 3/3: Quanto tempo você perde por dia com tarefas repetitivas?"
        },
        "chatbot": {
            1: "Pergunta 1/3: Para qual empresa/negócio você quer um chatbot? 💬",
            2: "Pergunta 2/3: Onde você quer o chatbot? (site, WhatsApp, Instagram, Facebook)",
            3: "Pergunta 3/3: Qual problema você quer resolver? (atendimento 24/7, qualificar leads, vendas)"
        },
        "ia": {
            1: "Pergunta 1/3: Qual é o nome do seu negócio? 🧠",
            2: "Pergunta 2/3: Qual processo você quer otimizar com IA? (atendimento, vendas, análise de dados, etc.)",
            3: "Pergunta 3/3: Você já usa alguma ferramenta de IA? Qual?"
        },
        
        # NICHOS DESENVOLVIMENTO WEB
        "sites": {
            1: "Pergunta 1/3: Qual é o nome da sua empresa/negócio? 🌐",
            2: "Pergunta 2/3: Qual é o objetivo do site? (vendas, portfólio, captação de leads, institucional)",
            3: "Pergunta 3/3: Você já tem um site? O que não está funcionando?"
        },
        "site_profissional": {
            1: "Pergunta 1/3: Qual é o nome da sua empresa? 🏢",
            2: "Pergunta 2/3: Qual é o foco do site? (vendas, branding, captar leads, e-commerce)",
            3: "Pergunta 3/3: Você já tem domínio e hospedagem? Precisa de integração com sistemas?"
        },
        "landing_page": {
            1: "Pergunta 1/3: Qual produto/serviço você quer vender? 🎯",
            2: "Pergunta 2/3: Você vai rodar tráfego pago para essa landing page? Qual plataforma?",
            3: "Pergunta 3/3: Qual é sua meta de conversão? Quantos leads você quer por mês?"
        },
        "sistema": {
            1: "Pergunta 1/3: Qual é o nome da sua empresa? ⚙️",
            2: "Pergunta 2/3: Que tipo de sistema você precisa? (gestão, vendas, agendamento, ERP, etc.)",
            3: "Pergunta 3/3: Você já usa planilhas ou outro sistema? O que não funciona nele?"
        },
        "app": {
            1: "Pergunta 1/3: Qual é o nome do seu app/ideia? 📱",
            2: "Pergunta 2/3: O app é para Android, iOS ou ambos?",
            3: "Pergunta 3/3: Qual problema seu app resolve? Quem é seu público-alvo?"
        },
        
        # NICHOS DESIGN
        "identidade_visual": {
            1: "Pergunta 1/3: Qual é o nome da sua empresa/marca? 🎨",
            2: "Pergunta 2/3: Você já tem logo ou vai criar do zero?",
            3: "Pergunta 3/3: Qual sentimento você quer passar? (confiança, luxo, jovem, inovador, etc.)"
        },
        "design": {
            1: "Pergunta 1/3: Qual é o nome da sua empresa? ✏️",
            2: "Pergunta 2/3: Que tipo de design você precisa? (posts, banners, flyers, artes para redes sociais)",
            3: "Pergunta 3/3: É para uma campanha específica ou uso contínuo?"
        },
        "logo": {
            1: "Pergunta 1/3: Qual é o nome da sua empresa/marca? 🏷️",
            2: "Pergunta 2/3: Qual segmento/nicho da sua empresa? (ex: tecnologia, saúde, alimentação)",
            3: "Pergunta 3/3: Você tem alguma referência de logo que você gosta?"
        },
        "branding": {
            1: "Pergunta 1/3: Qual é o nome da sua marca? 🎯",
            2: "Pergunta 2/3: Qual é o posicionamento que você quer ter no mercado? (premium, acessível, inovador)",
            3: "Pergunta 3/3: Quem é seu público-alvo? Como você quer ser visto por eles?"
        },
        
        # NICHOS CONSULTORIA
        "consultoria": {
            1: "Pergunta 1/3: Qual é o nome do seu negócio de consultoria? 📈",
            2: "Pergunta 2/3: Qual é seu maior desafio para atrair clientes?",
            3: "Pergunta 3/3: Você tem presença online? Site, redes sociais?"
        },
        
        # PÁGINAS GERAIS
        "portfolio": {
            1: "Pergunta 1/3: Qual é seu nome/nome artístico? 🎨",
            2: "Pergunta 2/3: Qual é sua área de atuação? (design, fotografia, desenvolvimento, etc.)",
            3: "Pergunta 3/3: Você já tem trabalhos publicados? Quer mostrar projetos ou captar clientes?"
        },
        "sobre": {
            1: "Pergunta 1/3: Qual é o nome da sua empresa? ℹ️",
            2: "Pergunta 2/3: Qual é sua história? Como começou seu negócio?",
            3: "Pergunta 3/3: O que te diferencia da concorrência?"
        },
        "contato": {
            1: "Pergunta 1/3: Qual é o nome da sua empresa? 📞",
            2: "Pergunta 2/3: Como você prefere que os clientes entrem em contato? (WhatsApp, e-mail, telefone)",
            3: "Pergunta 3/3: Você quer um formulário no site ou só informações de contato?"
        },
        "home": {
            1: "Pergunta 1/3: Qual é o nome da sua empresa? 🏠",
            2: "Pergunta 2/3: Qual é o principal objetivo da sua página inicial? (vendas, apresentação, branding)",
            3: "Pergunta 3/3: O que você quer destacar primeiro? (produtos, serviços, portfólio, formulário)"
        },
        
        # DEFAULT
        "default": {
            1: "Pergunta 1/3: Qual é o nome do seu negócio? 🎯",
            2: "Pergunta 2/3: Qual é seu principal desafio hoje?",
            3: "Pergunta 3/3: Você já investe em marketing digital ou presença online?"
        }
    }
    
    nicho_questions = questions.get(tag, questions["default"])
    return nicho_questions.get(question_num, "Conte-me mais sobre seu negócio...")

def generate_consultative_analysis(tag: str, name: str, business_name: str, challenge: str, digital_presence: str) -> str:
    """
    Gera análise consultiva personalizada baseada nas respostas do cliente
    """
    analyses = {
        "barbearia": f"""Perfeito, {name}! Analisando o que você me contou sobre {business_name}... 🔍

Identifiquei que você está enfrentando: {challenge}

📊 MINHA ANÁLISE PROFISSIONAL:

A maioria das barbearias que atendemos chegam com os mesmos problemas que você. E a solução NÃO é apenas um sistema - é um ECOSSISTEMA DIGITAL completo:

🎯 SOLUÇÃO PRINCIPAL:
**Sistema de Gestão para Barbearia**
- Agenda online 24/7 (acabou cliente ligando)
- Lembretes automáticos por WhatsApp (zero no-show)
- Controle financeiro completo
- Dashboard com tudo que você vende

Veja todos os detalhes aqui: https://fullstackdavi.github.io/DigitalSoluctions/produto-barbearia.html

💰 MAS AQUI ESTÁ O SEGREDO DOS BARBEIROS QUE MAIS LUCRAM:

Eles não param no sistema. Eles combinam com:

✅ **Gestão de Instagram Profissional**
Porque não adianta ter horário vago se ninguém sabe da sua barbearia. Posts de cortes todos os dias = fila de espera

✅ **Tráfego Pago Local**  
Google Ads mostrando SUA barbearia quando alguém procura "barbearia perto de mim". Agenda lotada em 15 dias.

✅ **Landing Page de Promoção**
"Primeiro corte por R$ 20" - captura WhatsApp e enche sua agenda de clientes novos

Esse é o COMBO que faz barbearia faturar 3x mais. Quer ver um case de sucesso?""",

        "restaurante": f"""Perfeito, {name}! Analisando o que você me contou sobre {business_name}... 🔍

Vi que você está com: {challenge}

📊 MINHA ANÁLISE PROFISSIONAL:

Restaurantes que mais crescem hoje têm UMA COISA em comum: presença digital forte. Não é só ter Instagram - é ter um SISTEMA.

🎯 SOLUÇÃO PRINCIPAL:
**Sistema Meatz para Restaurantes**
- Cardápio digital interativo  
- Pedidos direto pelo site (sem taxa de iFood)
- Dashboard de vendas em tempo real
- Gestão completa do delivery

Veja todos os detalhes aqui: https://fullstackdavi.github.io/DigitalSoluctions/produto-meatz.html

💰 MAS O SEGREDO DOS RESTAURANTES QUE DOMINAM:

✅ **Identidade Visual Profissional**
Logo, cardápio bonito, fotos dos pratos - você não está competindo com o bar da esquina, está competindo com iFood

✅ **Gestão de Instagram**
3 posts por dia com os pratos = delivery lotado. Não é exagero, é estratégia

✅ **Tráfego Pago para Delivery**
Facebook Ads mostrando seu prato pra quem está com fome AGORA. ROI de 400% é normal.

✅ **Landing Page de Promoção**
"2 por 1 às quartas" - captura contato e fideliza cliente

Esse combo faz restaurante sair do prejuízo para 6 dígitos/mês. Quer que eu te mostre como?""",

        "hamburgueria": f"""Perfeito, {name}! Analisando o que você me contou sobre {business_name}... 🔍

Vi que você está com: {challenge}

📊 MINHA ANÁLISE PROFISSIONAL:

Hamburguerias que mais crescem hoje têm UMA COISA em comum: presença digital forte. Não é só ter Instagram - é ter um SISTEMA.

🎯 SOLUÇÃO PRINCIPAL:
**Sistema Meatz para Hamburguerias**
- Cardápio digital interativo com fotos dos burgers
- Pedidos direto pelo site (sem taxa de iFood)
- Dashboard de vendas em tempo real
- Gestão completa do delivery

Veja todos os detalhes aqui: https://fullstackdavi.github.io/DigitalSoluctions/produto-meatz.html

💰 MAS O SEGREDO DAS HAMBURGUERIAS QUE DOMINAM:

✅ **Identidade Visual Profissional**
Logo, cardápio bonito, fotos dos burgers - você não está competindo com o lanche da esquina, está competindo com iFood

✅ **Gestão de Instagram**
3 posts por dia com os burgers = delivery lotado. Não é exagero, é estratégia

✅ **Tráfego Pago para Delivery**
Facebook/Instagram Ads mostrando seu burger pra quem está com fome AGORA. ROI de 400% é normal.

✅ **Landing Page de Promoção**
"Combo especial hoje" - captura contato e fideliza cliente

Esse combo faz hamburgueria sair do zero para 6 dígitos/mês. Quer que eu te mostre como?""",
    }
    
    # Análise genérica para nichos não mapeados
    default_analysis = f"""Perfeito, {name}! Analisando o que você me contou sobre {business_name}... 🔍

Vi que você está enfrentando: {challenge}

📊 MINHA ANÁLISE PROFISSIONAL:

Empresas que mais crescem hoje combinam 3 pilares:

🎯 PRESENÇA DIGITAL PROFISSIONAL:
- Site/Sistema personalizado
- Identidade visual forte
- Redes sociais ativas

💰 ATRAÇÃO DE CLIENTES:
- Tráfego pago estratégico
- Landing pages que convertem
- SEO para aparecer no Google

🤖 AUTOMAÇÃO E EFICIÊNCIA:
- Chatbots inteligentes
- Processos automatizados
- Atendimento 24/7

Com base no que você me contou, vou montar um pacote personalizado para {business_name}. Quer ver a proposta?"""

    return analyses.get(tag, default_analysis)

@app.route('/')
def index():
    tag = request.args.get('tag', 'default')
    session['tag'] = tag
    session['step'] = 'name'
    session.pop('name', None)
    session.pop('phone', None)
    
    nicho_nome = NICHO_MENSAGENS.get(tag, NICHO_MENSAGENS['default'])
    
    return render_template('chat.html', tag=tag, nicho_nome=nicho_nome)

@app.route('/start', methods=['POST'])
def start():
    data = request.json
    if not data:
        return jsonify({'success': False, 'response': 'Dados inválidos.'})
    
    message = data.get('message', '').strip()
    step = session.get('step', 'name')
    current_name = session.get('name')
    
    if not message:
        return jsonify({
            'success': False,
            'response': 'Por favor, digite uma mensagem.'
        })
    
    info = extract_user_info(message, step, current_name)
    
    if step == 'choose_niche':
        message_lower = message.lower()
        
        nicho_keywords = {
            'barbearia': ['barbearia', 'barbeiro', 'salão', 'corte', 'cabelo'],
            'restaurante': ['restaurante', 'comida', 'delivery', 'cardápio', 'garçom'],
            'hamburgueria': ['hamburgueria', 'burger', 'hamburguer', 'lanche', 'sanduíche'],
            'ecommerce': ['loja', 'ecommerce', 'e-commerce', 'vendas online', 'vender online'],
            'marketing': ['marketing', 'digital', 'divulgação', 'propaganda'],
            'trafego_pago': ['tráfego', 'anúncios', 'ads', 'google ads', 'facebook ads'],
            'sites': ['site', 'website', 'página', 'criar site'],
            'identidade_visual': ['logo', 'identidade', 'marca', 'visual', 'branding'],
            'automacao': ['automação', 'automatizar', 'processos'],
            'chatbot': ['chatbot', 'bot', 'atendimento automático'],
            'consultoria': ['consultoria', 'consultor', 'assessoria']
        }
        
        detected_niche = None
        for niche, keywords in nicho_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_niche = niche
                break
        
        if detected_niche:
            session['tag'] = detected_niche
            session['step'] = 'qualification_1'
            nicho_nome = NICHO_MENSAGENS.get(detected_niche, 'soluções digitais')
            name = session.get('name', 'Usuário')
            
            qualification_questions = get_qualification_question(detected_niche, 1)
            
            return jsonify({
                'success': True,
                'response': f'Perfeito! Vejo que você tem interesse em {nicho_nome}. 🎯\n\nAgora vou fazer 3 perguntas rápidas para entender melhor seu negócio e montar a solução ideal para você.\n\n{qualification_questions}',
                'step': 'qualification_1'
            })
        else:
            return jsonify({
                'success': False,
                'response': '''Não consegui identificar seu nicho. Por favor, escolha uma das opções:

📌 **NEGÓCIOS LOCAIS:**
• Barbearia
• Restaurante / Hamburgueria

💼 **EMPRESAS & VENDAS:**
• E-commerce / Loja Online
• Consultoria

🎨 **DESIGN & MARKETING:**
• Marketing Digital
• Tráfego Pago (Google Ads, Facebook Ads)
• Identidade Visual / Logo

💻 **TECNOLOGIA:**
• Sites e Sistemas
• Automação
• Chatbot

Digite qual área te interessa!'''
            })
    
    elif step == 'name':
        extracted_name = info.get('name')
        extracted_phone = info.get('phone')
        
        if extracted_name:
            if len(extracted_name) < 2:
                return jsonify({
                    'success': False,
                    'response': 'Por favor, digite um nome válido com pelo menos 2 caracteres.'
                })
            
            if len(extracted_name) > 100:
                return jsonify({
                    'success': False,
                    'response': 'Por favor, digite um nome com no máximo 100 caracteres.'
                })
            
            session['name'] = extracted_name
            
            if extracted_phone:
                phone_clean = re.sub(r'[^\d]', '', extracted_phone)
                
                if len(phone_clean) >= 10 and len(phone_clean) <= 11:
                    session['phone'] = phone_clean
                    session['step'] = 'chat'
                    tag = session.get('tag', 'default')
                    save_lead(extracted_name, phone_clean, tag)
                    
                    return jsonify({
                        'success': True,
                        'response': f'Perfeito, {extracted_name}! Entendi que seu nome é {extracted_name} e seu telefone é {phone_clean}. Seus dados foram registrados com sucesso! Como posso ajudá-lo hoje?',
                        'step': 'chat'
                    })
            
            session['step'] = 'phone'
            return jsonify({
                'success': True,
                'response': f'Prazer em conhecê-lo, {extracted_name}! Agora, por favor, informe seu número de telefone (com DDD):',
                'step': 'phone'
            })
        else:
            return jsonify({
                'success': False,
                'response': 'Desculpe, não consegui identificar seu nome. Por favor, me diga seu nome de forma clara. Exemplo: "Meu nome é João" ou apenas "João".'
            })
    
    elif step == 'phone':
        extracted_phone = info.get('phone') if info.get('phone') else message
        phone_clean = re.sub(r'[^\d]', '', extracted_phone)
        
        if not phone_clean:
            return jsonify({
                'success': False,
                'response': 'Por favor, digite seu número de telefone.'
            })
        
        if len(phone_clean) < 10 or len(phone_clean) > 11:
            return jsonify({
                'success': False,
                'response': 'Por favor, digite um número de telefone válido com DDD (10 ou 11 dígitos). Exemplo: 11987654321'
            })
        
        session['phone'] = phone_clean
        
        name = session.get('name', 'Usuário')
        tag = session.get('tag', 'default')
        
        save_lead(name, phone_clean, tag)
        
        # Se tag é default, pedir para escolher nicho
        if tag == 'default':
            session['step'] = 'choose_niche'
            return jsonify({
                'success': True,
                'response': f'''Perfeito, {name}! Seus dados foram registrados. 📋

Vejo que você não escolheu uma área de atuação específica.

Para te atender melhor, qual área você tem interesse?

📌 **NEGÓCIOS LOCAIS:**
• Barbearia
• Restaurante / Hamburgueria

💼 **EMPRESAS & VENDAS:**
• E-commerce / Loja Online
• Consultoria

🎨 **DESIGN & MARKETING:**
• Marketing Digital
• Tráfego Pago (Google Ads, Facebook Ads)
• Identidade Visual / Logo

💻 **TECNOLOGIA:**
• Sites e Sistemas
• Automação
• Chatbot

Digite qual área te interessa! 👇''',
                'step': 'choose_niche'
            })
        else:
            # Se já tem tag, continua com qualificação
            session['step'] = 'qualification_1'
            qualification_questions = get_qualification_question(tag, 1)
            
            return jsonify({
                'success': True,
                'response': f'Perfeito, {name}! Seus dados foram registrados. 📋\n\nAgora vou fazer 3 perguntas rápidas para entender melhor seu negócio e montar a solução ideal para você.\n\n{qualification_questions}',
                'step': 'qualification_1'
            })
    
    elif step == 'qualification_1':
        session['q1_answer'] = message
        session['step'] = 'qualification_2'
        tag = session.get('tag', 'default')
        question = get_qualification_question(tag, 2)
        
        return jsonify({
            'success': True,
            'response': question,
            'step': 'qualification_2'
        })
    
    elif step == 'qualification_2':
        session['q2_answer'] = message
        session['step'] = 'qualification_3'
        tag = session.get('tag', 'default')
        question = get_qualification_question(tag, 3)
        
        return jsonify({
            'success': True,
            'response': question,
            'step': 'qualification_3'
        })
    
    elif step == 'qualification_3':
        session['q3_answer'] = message
        session['step'] = 'chat'
        
        # Gera análise consultiva baseada nas respostas
        tag = session.get('tag', 'default')
        name = session.get('name', 'Usuário')
        q1 = session.get('q1_answer', '')
        q2 = session.get('q2_answer', '')
        q3 = session.get('q3_answer', '')
        
        analysis = generate_consultative_analysis(tag, name, q1, q2, q3)
        
        return jsonify({
            'success': True,
            'response': analysis,
            'step': 'chat'
        })
    
    return jsonify({'success': False, 'response': 'Erro no processamento.'})

@app.route('/chat_ai', methods=['POST'])
def chat_ai():
    data = request.json
    if not data:
        return jsonify({'success': False, 'response': 'Dados inválidos.'})
    
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({
            'success': False,
            'response': 'Por favor, envie uma mensagem.'
        })
    
    tag = session.get('tag', None)
    user_name = session.get('name', None)
    
    # Identifica automaticamente o produto mencionado ANTES da IA
    produto_identificado = get_product_link(message)
    
    # Gera a resposta da IA
    ai_response = ask_gemini(message, tag, user_name)
    
    # Se identificou um produto, SEMPRE sobrescreve/adiciona o link correto
    if produto_identificado and produto_identificado in PRODUTO_LINKS:
        link = PRODUTO_LINKS[produto_identificado]
        
        # Remove qualquer link genérico que veio do fallback da IA
        if "https://fullstackdavi.github.io/DigitalSoluctions/" in ai_response and "produto-" not in ai_response:
            # Remove o link genérico
            ai_response = ai_response.split("https://fullstackdavi.github.io/DigitalSoluctions/")[0].strip()
            # Remove possíveis dois pontos ou textos finais
            if ai_response.endswith(":"):
                ai_response = ai_response[:-1].strip()
        
        # Adiciona o link correto do produto
        if link not in ai_response:
            ai_response += f"\n\nVeja todos os detalhes aqui: {link}"
    
    return jsonify({
        'success': True,
        'response': ai_response
    })

@app.route('/redirect')
def redirect_user():
    tag = session.get('tag', 'default')
    url = NICHO_URLS.get(tag, NICHO_URLS['default'])
    return render_template('thankyou.html', redirect_url=url, tag=tag)

@app.route('/export_leads')
def export_leads():
    """Exporta todos os leads para um arquivo CSV"""
    import csv
    from io import StringIO
    from flask import Response
    from db_init import get_all_leads
    
    # Busca todos os leads
    leads = get_all_leads()
    
    # Cria o CSV em memória
    output = StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow(['ID', 'Nome', 'Telefone', 'Tag/Nicho', 'Data de Cadastro'])
    
    # Dados
    for lead in leads:
        writer.writerow(lead)
    
    # Prepara o arquivo para download
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=leads_digital_soluctions.csv'
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
