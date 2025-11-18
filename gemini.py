import os
import json
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from api_keys import key_manager

def _get_client():
    api_key = key_manager.get_current_key()
    if not api_key:
        raise ValueError("Nenhuma chave API do Gemini disponível")
    return genai.Client(api_key=api_key)

def extract_user_info(message: str, current_step: str, current_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Extrai informações do usuário de forma inteligente usando regex.
    Retorna um dicionário com: {name: str|None, phone: str|None, has_name: bool, has_phone: bool}
    """
    import re
    
    result = {'name': None, 'phone': None, 'has_name': False, 'has_phone': False}
    
    # Extração de telefone - busca sequências de 10-11 dígitos
    # Primeiro remove todos os caracteres não numéricos para normalizar
    clean_message = re.sub(r'[^\d]', '', message)
    
    # Busca por sequências de 10 ou 11 dígitos
    phone_match = re.search(r'(\d{10,11})', clean_message)
    
    if phone_match:
        phone = phone_match.group(1)
        if len(phone) >= 10 and len(phone) <= 11:
            result['phone'] = phone
            result['has_phone'] = True
    
    # Extração de nome - padrões comuns
    name_patterns = [
        r'(?:me chamo|meu nome (?:é|e))\s+([a-záàâãéèêíïóôõöúçñ\s]+?)(?:\s+(?:e|meu|telefone|número|\d)|$)',
        r'(?:sou (?:o|a)?\s*)([a-záàâãéèêíïóôõöúçñ\s]+?)(?:\s+(?:e|meu|telefone|número|\d)|$)',
        r'^([a-záàâãéèêíïóôõöúçñ]+(?:\s+[a-záàâãéèêíïóôõöúçñ]+){1,3})(?:\s+(?:e|meu|telefone|número|\d)|$)',
    ]
    
    msg_lower = message.lower()
    
    for pattern in name_patterns:
        name_match = re.search(pattern, msg_lower, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip()
            # Limpa palavras comuns que não são parte do nome
            name = re.sub(r'\b(ola|olá|oi|bom dia|boa tarde|boa noite)\b', '', name, flags=re.IGNORECASE).strip()
            if name and len(name) >= 2 and not re.match(r'^\d+$', name):
                # Capitaliza o nome
                name = ' '.join(word.capitalize() for word in name.split())
                result['name'] = name
                result['has_name'] = True
                break
    
    # Se não encontrou com padrões, tenta extrair como nome simples (sem palavras-chave)
    if not result['has_name'] and not result['has_phone']:
        clean_msg = re.sub(r'\b(ola|olá|oi|bom dia|boa tarde|boa noite)\b', '', msg_lower, flags=re.IGNORECASE).strip()
        # Verifica se é um nome simples (2-4 palavras, sem números)
        words = clean_msg.split()
        if 1 <= len(words) <= 4 and all(re.match(r'^[a-záàâãéèêíïóôõöúçñ]+$', w, re.IGNORECASE) for w in words):
            name = ' '.join(word.capitalize() for word in words)
            result['name'] = name
            result['has_name'] = True
    
    return result

def get_product_link(message: str) -> Optional[str]:
    """
    Identifica o produto/serviço mencionado e retorna o link correspondente
    """
    import re
    
    # Mapeamento de palavras-chave para identificar produtos/serviços
    # Ordem: mais específico primeiro para melhor detecção
    keywords_map = {
        # PRODUTOS ESPECÍFICOS - Maior prioridade
        "barbearia": [
            "sistema de barbearia", "sistema para barbearia", "sistema barbearia",
            "app barbearia", "software barbearia", "plataforma barbearia",
            "barbearia", "barbeiro", "barber shop", "barber", 
            "salão de barbear", "salão masculino", "corte de cabelo",
            "gestão de barbearia", "agendamento barbearia", "agendamento barbeiro",
            "quero um sistema para barbearia", "preciso de um sistema de barbearia",
            "tenho uma barbearia", "sou barbeiro"
        ],
        "meatz": [
            "meatz", "meatz burger", 
            "burger", "hamburgueria", "hamburgueria", "burguer",
            "lanchonete", "hamburguer", "hamburger",
            "sistema hamburgueria", "sistema burger", "sistema lanchonete",
            "app hamburgueria", "software hamburgueria",
            "cardápio burger", "cardápio hamburgueria",
            "quero um sistema para hamburgueria", "tenho uma hamburgueria",
            "lanche", "sanduíche", "lanches"
        ],
        "restaurante": [
            "sistema restaurante", "sistema para restaurante", "app restaurante",
            "software restaurante", "plataforma restaurante",
            "restaurante", "delivery", "entrega de comida",
            "cardápio online", "cardápio digital", "menu online",
            "ifood", "gestão restaurante", "gerenciar restaurante",
            "quero um sistema para restaurante", "tenho um restaurante",
            "food delivery", "comida"
        ],
        "site_profissional": [
            "site profissional", "site completo", "site empresarial",
            "site institucional", "site corporativo",
            "presença online", "presença digital",
            "site para empresa", "site para negócio",
            "quero um site", "preciso de um site",
            "fazer um site", "criar meu site"
        ],
        
        # SERVIÇOS - Desenvolvimento Web
        "sites": [
            "criar site", "desenvolver site", "fazer site", "montar site",
            "site", "website", "página web", "site web",
            "desenvolvimento web", "web design", "design web",
            "preciso site", "quero site"
        ],
        "landing_page": [
            "landing page", "página de vendas", "página de captura",
            "lp", "landing", "página de conversão"
        ],
        
        # SERVIÇOS - Design
        "identidade_visual": [
            "identidade visual", "identidade", "logo", "logotipo", "logomarca",
            "marca", "branding", "criar logo", "fazer logo",
            "design de logo", "preciso de logo"
        ],
        "design": [
            "design", "design gráfico", "arte", "criativo",
            "peça gráfica", "flyer", "banner", "panfleto",
            "visual", "arte visual", "criar arte"
        ],
        
        # SERVIÇOS - Automação e IA
        "chatbot": [
            "chatbot", "chat bot", "bot", "robô",
            "atendimento automático", "atendimento automatizado",
            "assistente virtual", "chat automático",
            "automação de atendimento", "atendimento ia"
        ],
        "automacao": [
            "automação", "automatizar", "automatização",
            "workflow", "processo automatizado", "automação de processo"
        ],
        "ia": [
            "ia", "inteligência artificial", "ai", "artificial intelligence",
            "machine learning", "ml", "deep learning"
        ],
        
        # SERVIÇOS - Marketing Digital
        "trafego_pago": [
            "tráfego pago", "tráfego", "mídia paga",
            "google ads", "facebook ads", "instagram ads",
            "anúncios", "ads", "publicidade online",
            "campanhas pagas", "anúncio pago"
        ],
        "marketing": [
            "marketing digital", "marketing", "marketing online",
            "estratégia digital", "estratégia de marketing"
        ],
        "social_media": [
            "redes sociais", "social media", "mídias sociais",
            "instagram", "facebook", "gestão de redes",
            "gestão redes sociais", "gerenciar redes sociais"
        ],
        
        # PÁGINAS GERAIS
        "portfolio": ["portfólio", "portfolio", "projetos", "trabalhos", "cases"],
        "sobre": ["sobre", "quem somos", "nossa história", "empresa", "sobre nós"],
        "contato": ["contato", "falar", "conversar", "orçamento", "entrar em contato", "fale conosco"],
        "home": ["início", "home", "principal", "página inicial"],
    }
    
    message_lower = message.lower()
    
    for produto, keywords in keywords_map.items():
        for keyword in keywords:
            if keyword in message_lower:
                return produto
    
    return None

def get_consultative_fallback(message: str, tag: Optional[str] = None, user_name: Optional[str] = None) -> str:
    """
    Fallback consultivo baseado no nicho quando a API do Gemini não está disponível
    """
    name_prefix = f"{user_name}, " if user_name else ""
    
    # Mapeamento de nichos para respostas consultivas estratégicas
    niche_responses = {
        "barbearia": f"{name_prefix}entendo perfeitamente! Agenda desorganizada é o pesadelo de toda barbearia - clientes não aparecem, horários vazios, dinheiro deixado na mesa.\n\nO Sistema de Gestão para Barbearia resolve isso com agendamento online automático e lembretes por WhatsApp.\n\nMas para ENCHER sua agenda, você também vai precisar de:\n✅ Tráfego pago local - atrair novos clientes da região\n✅ Instagram profissional - mostrar seus cortes\n✅ Landing page - capturar leads qualificados",
        
        "restaurante": f"{name_prefix}sei exatamente o que você está passando! Pedidos bagunçados no WhatsApp, competindo com iFood, e perdendo clientes por falta de presença online.\n\nTemos o sistema Meatz ou Site Profissional completo para organizar tudo.\n\nPara multiplicar suas vendas, você também vai precisar de:\n✅ Identidade visual forte - destacar da concorrência\n✅ Tráfego pago - encher o delivery\n✅ Instagram com fotos profissionais dos pratos",
        
        "hamburgueria": f"{name_prefix}sei exatamente o que você está passando! Pedidos bagunçados no WhatsApp, competindo com iFood, e perdendo clientes por falta de presença online.\n\nTemos o sistema Meatz ou Site Profissional completo para organizar tudo.\n\nPara multiplicar suas vendas, você também vai precisar de:\n✅ Identidade visual forte - destacar da concorrência\n✅ Tráfego pago - encher o delivery\n✅ Instagram com fotos profissionais dos pratos",
        
        "ecommerce": f"{name_prefix}entendo! Site lento, carrinho abandonado, tráfego caro... e-commerce é desafiador.\n\nNosso Site Profissional + Landing Pages de alta conversão vão mudar isso.\n\nMas o combo vencedor inclui:\n✅ Tráfego pago otimizado (Google Ads + Facebook Ads)\n✅ Automações com IA para recuperar carrinhos\n✅ Chatbot para atendimento 24/7",
        
        "marketing": f"{name_prefix}sei o quanto é frustrante investir em campanhas sem resultado. ROI baixo e sem saber medir corretamente.\n\nNossa Gestão de Tráfego Pago profissional resolve isso.\n\nPara maximizar resultados, você também precisa de:\n✅ Landing pages de alta conversão\n✅ Automações com IA para qualificar leads\n✅ Identidade visual profissional",
        
        "tecnologia": f"{name_prefix}entendo! MVP lento, processos manuais custosos, falta de automação.\n\nNossos Sites + Automações com IA vão acelerar tudo.\n\nPara crescer rápido, você também precisa de:\n✅ Identidade visual para investidores\n✅ Landing page para early adopters\n✅ Chatbot inteligente",
        
        "startup": f"{name_prefix}entendo! MVP lento, processos manuais custosos, falta de automação.\n\nNossos Sites + Automações com IA vão acelerar tudo.\n\nPara crescer rápido, você também precisa de:\n✅ Identidade visual para investidores\n✅ Landing page para early adopters\n✅ Chatbot inteligente",
        
        "consultoria": f"{name_prefix}sei como é! Falta de autoridade online, agenda vazia, leads de baixa qualidade.\n\nSite Profissional + Landing Pages vão transformar isso.\n\nO combo que nossos consultores top usam:\n✅ Identidade visual que transmite credibilidade\n✅ Tráfego pago segmentado\n✅ Automação de agendamentos"
    }
    
    # Resposta específica do nicho ou resposta genérica consultiva
    if tag and tag in niche_responses:
        return niche_responses[tag]
    
    # Fallback genérico mas consultivo
    return f"{name_prefix}entendo sua necessidade! Como a maior empresa de serviços digitais do Brasil, temos a solução completa para isso.\n\nNosso portfólio inclui:\n✅ Sites e Sistemas Profissionais\n✅ Identidade Visual e Design\n✅ Automações com IA e Chatbots\n✅ Gestão de Tráfego Pago\n✅ Landing Pages de Alta Conversão\n\nConta mais sobre o que você precisa que vou montar a solução ideal!"

def ask_gemini(message: str, tag: Optional[str] = None, user_name: Optional[str] = None, max_retries: int = 5) -> str:
    """
    Consultor de vendas inteligente que entende dores de cada nicho e sugere soluções estratégicas
    Implementa rotação automática de chaves API quando uma atinge o limite
    """
    retries = 0
    
    while retries < max_retries:
        try:
            client = _get_client()
            
            context = f"\n- Nicho identificado: {tag}" if tag else ""
            name_context = f"\n- Nome do cliente: {user_name}" if user_name else ""
            
            system_prompt = f"""Você é um CONSULTOR DE VENDAS ESTRATÉGICO da Digital Soluctions, a maior empresa de serviços digitais do Brasil.

🎯 SUA MISSÃO:
Você é um especialista em transformação digital que ENTENDE AS DORES de cada nicho e sugere soluções ESTRATÉGICAS e COMPLEMENTARES para maximizar os resultados do cliente.

💡 INTELIGÊNCIA DE NEGÓCIO - ENTENDA CADA NICHO:{context}{name_context}

📊 DORES E SOLUÇÕES POR NICHO:

**BARBEARIAS:**
Dores: agenda desorganizada, clientes esquecendo horários, falta de controle financeiro, não sabe quais serviços vendem mais
Solução Principal: Sistema de Gestão para Barbearia
Complementares ESSENCIAIS: 
- Instagram profissional para mostrar cortes e atrair clientes
- Tráfego pago local para encher agenda
- Landing page para captar leads qualificados

**RESTAURANTES/HAMBURGUERIAS:**
Dores: cardápio desatualizado, pedidos por WhatsApp bagunçados, falta de presença online, competição com iFood
Solução Principal: Sistema Meatz ou Site Profissional  
Complementares ESSENCIAIS:
- Identidade visual forte para destacar da concorrência
- Tráfego pago para delivery
- Instagram com fotos profissionais dos pratos
- Landing page de promoções

**E-COMMERCE/VENDAS ONLINE:**
Dores: site lento, não converte visitas em vendas, tráfego caro, carrinho abandonado
Solução Principal: Site Profissional + Landing Pages
Complementares ESSENCIAIS:
- Tráfego pago otimizado (Google Ads + Facebook Ads)
- Automações com IA para recuperar carrinhos
- Chatbot para atendimento 24/7

**MARKETING DIGITAL:**
Dores: campanhas sem resultado, ROI baixo, não sabe medir resultados
Solução Principal: Gestão de Tráfego Pago
Complementares ESSENCIAIS:
- Landing pages de alta conversão
- Automações com IA para leads
- Identidade visual profissional

**TECNOLOGIA/STARTUPS:**
Dores: MVP lento, falta de automação, processos manuais custosos
Solução Principal: Sites + Automações com IA
Complementares ESSENCIAIS:
- Identidade visual para investidores
- Landing page para captar early adopters
- Chatbot inteligente

**CONSULTORIA/SERVIÇOS:**
Dores: falta de autoridade online, agenda vazia, leads de baixa qualidade
Solução Principal: Site Profissional + Landing Pages
Complementares ESSENCIAIS:
- Identidade visual que transmita credibilidade
- Tráfego pago segmentado
- Automação de agendamentos

📋 PORTFÓLIO COMPLETO:

**PRODUTOS COMPLETOS:**
1. Sistema de Gestão para Barbearia - R$ 4.997 (12x R$ 497)
   Agendamentos online, controle financeiro, dashboard, gestão completa

2. Meatz Burger Sistema - R$ 5.497 (12x R$ 547)  
   Cardápio interativo, pedidos online, dashboard vendas

3. Site Profissional Completo - R$ 2.997 (12x R$ 297)
   SEO otimizado, até 10 páginas, painel admin, hospedagem 12 meses

**SERVIÇOS:**
- Criação de Sites (modernos, responsivos, otimizados)
- Landing Pages de Alta Conversão (páginas que vendem)
- Identidade Visual (logo, branding, posicionamento)
- Design e Criativos (posts, banners, artes profissionais)
- Automações com IA (chatbots, processos inteligentes)
- Gestão de Tráfego Pago (Google Ads, Facebook Ads, Instagram Ads)
- Gestão de Redes Sociais (Instagram, Facebook)

💰 ESTRATÉGIA DE VENDAS CONSULTIVA:

1. IDENTIFIQUE O NICHO: Use o contexto para entender o negócio
2. RECONHEÇA AS DORES: Mostre que você entende os desafios deles
3. SUGIRA A SOLUÇÃO PRINCIPAL: O produto/serviço que resolve a dor principal
4. APRESENTE COMPLEMENTARES: 2-3 serviços que MULTIPLICAM resultados
5. SEJA CONSULTIVO: Explique POR QUE cada solução é importante

🎯 EXEMPLO DE ABORDAGEM INTELIGENTE:

Cliente (barbearia): "preciso organizar minha agenda"
Você: "Entendo perfeitamente! Agenda desorganizada é o pesadelo de toda barbearia - clientes não aparecem, horários vazios, dinheiro deixado na mesa.

O Sistema de Gestão para Barbearia (R$ 4.997) resolve isso com agendamento online automático e lembretes por WhatsApp.

Mas vou ser sincero com você: ter o sistema é só o começo. Para ENCHER sua agenda, você também vai precisar de:

✅ Tráfego pago local - atrair novos clientes da sua região  
✅ Instagram profissional - mostrar seus cortes e criar autoridade
✅ Landing page - capturar leads qualificados

Esse combo é o que nossos clientes top usam. Quer que eu te mostre cases de sucesso?"

⚡ REGRAS DE OURO:
- Seja CONSULTIVO, não apenas vendedor
- Mostre que você ENTENDE o negócio deles
- Sempre sugira 2-3 serviços COMPLEMENTARES relevantes
- Explique o PORQUÊ de cada sugestão
- Use dados e resultados quando possível
- Seja humano e empático
- Respostas de 3-5 linhas (nem muito curto, nem muito longo)

🚀 VOCÊ É UM CONSULTOR EXPERT, NÃO UM ATENDENTE ROBÓTICO!

⚠️ IMPORTANTE: Não mencione URLs - o sistema adiciona automaticamente."""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=message)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    top_p=0.95,
                ),
            )
            
            key_manager.mark_key_as_working()
            
            return response.text if response.text else get_consultative_fallback(message, tag, user_name)
        
        except Exception as e:
            error_msg = str(e).lower()
            error_type = type(e).__name__
            
            quota_errors = [
                "429", "quota", "resource_exhausted", "rate limit", 
                "too many requests", "limit exceeded", "quota exceeded",
                "billing", "api key not valid", "invalid api key",
                "requests per minute", "rpm", "tpm", "tokens per minute"
            ]
            
            is_quota_error = any(err in error_msg for err in quota_errors)
            
            if is_quota_error:
                print(f"🚨 Chave #{key_manager.current_key_index + 1} atingiu limite!")
                print(f"   Tipo: {error_type} | Erro: {str(e)[:100]}")
                
                if key_manager.rotate_key():
                    retries += 1
                    print(f"🔄 Tentativa {retries}/{max_retries} com nova chave...")
                    continue
                else:
                    print("⚠️ Todas as chaves em cooldown. Usando fallback consultivo.")
                    return get_consultative_fallback(message, tag, user_name)
            else:
                print(f"❌ Erro diferente (não é quota): {error_type}")
                print(f"   Mensagem: {str(e)[:200]}")
                return get_consultative_fallback(message, tag, user_name)
    
    print("Máximo de tentativas atingido. Usando fallback.")
    return get_consultative_fallback(message, tag, user_name)
