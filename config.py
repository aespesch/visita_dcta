"""
Configuration file for the DCTA visitor registration system.
This centralizes all settings that might need to be changed without modifying the main code.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (for sensitive data)
load_dotenv()

# Event Information
EVENT_NAME = "Visita ao DCTA - Turma ITA 90"
EVENT_DATE = "29 de novembro de 2025 às 09:00"
EVENT_LOCATION = "DCTA (antigo CTA), São José dos Campos - SP"

# Data Source Configuration
# Path to the CSV file containing participant information
PARTICIPANTS_FILE = "participants.csv"

# User Interface Messages
# Customize these messages to match your event's tone
MESSAGES = {
    "welcome": f"Bem-vindo ao sistema de registro para {EVENT_NAME}!",
    "not_found": "Nome não encontrado na lista de convidados. Verifique se digitou corretamente ou entre em contato com a organização.",
    "registration_success": """
    **Registro realizado com sucesso!**
    
    **Importante:**
    - Chegue com 30 minutos de antecedência
    - Todos os visitantes devem portar documento de identidade com foto
    - Menores de idade devem estar acompanhados dos responsáveis
    """,
    "invalid_rg": "RG inválido. Por favor, digite apenas números."
}

# Guest Limits
# Maximum number of companions allowed when not specified in the CSV
MAX_COMPANIONS = 10

# Application Settings
# Page configuration for Streamlit
PAGE_CONFIG = {
    "page_title": f"Registro de Visitantes - {EVENT_NAME}",
    "page_icon": "🏛️",
    "layout": "centered",
    "initial_sidebar_state": "collapsed"
}

# Admin Configuration
# Password for accessing the admin dashboard
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # Change this in production!

# Security Notice
SECURITY_NOTICE = """
**Aviso de Segurança:**
Os dados coletados serão utilizados exclusivamente para autorização de acesso ao DCTA.
Ao prosseguir, você autoriza o compartilhamento destas informações com a segurança do DCTA.
"""