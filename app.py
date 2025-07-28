"""
Visitor Registration System for DCTA - Main Application
A web system for managing visitor registration for military base access.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import unicodedata
import re
import uuid
from config import *


# Page configuration
st.set_page_config(**PAGE_CONFIG)

# Initialize session state
if 'confirmed' not in st.session_state:
    st.session_state.confirmed = False
if 'participant_data' not in st.session_state:
    st.session_state.participant_data = None
if 'show_registration' not in st.session_state:
    st.session_state.show_registration = False
if 'total_participants' not in st.session_state:
    st.session_state.total_participants = 0
if 'visitors_data' not in st.session_state:
    st.session_state.visitors_data = []

def normalize_name(name):
    """
    Normalize name for comparison by removing accents, extra spaces, 
    and converting to lowercase.
    """
    # If name is not a string, return empty string
    if not isinstance(name, str):
        return ""
    
    # Remove leading/trailing spaces
    name = name.strip()
    
    if name == "":
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Normalize to decomposed form and remove accents
    name = unicodedata.normalize('NFKD', name)
    name = ''.join([c for c in name if not unicodedata.combining(c)])
    
    # Remove non-alphanumeric characters except spaces
    name = re.sub(r'[^a-z0-9\s]', '', name)
    
    # Replace multiple spaces with single space
    name = re.sub(r'\s+', ' ', name)
    
    return name

def load_participants():
    """Load participants from CSV file."""
    try:
        # Try common encodings for Portuguese
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(PARTICIPANTS_FILE, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
            except Exception:
                continue
        
        if df is None:
            st.error("❌ Não foi possível carregar o arquivo com nenhuma codificação testada.")
            return pd.DataFrame()
        
        return df
    
    except FileNotFoundError:
        st.error(f"❌ Arquivo não encontrado: {PARTICIPANTS_FILE}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro inesperado ao carregar o arquivo: {str(e)}")
        return pd.DataFrame()

def find_participant(name, participants_df):
    """Find participant in the list with flexible name matching."""
    normalized_input = normalize_name(name)
    
    if participants_df.empty:
        st.warning("⚠️ A lista de participantes está vazia.")
        return None
    
    # Iterate over each row in the dataframe
    for idx, row in participants_df.iterrows():
        if 'full_name' in row:
            original_db_name = row['full_name']
            normalized_db_name = normalize_name(original_db_name)
            
            if normalized_input == normalized_db_name:
                st.success(f"✅ Bem-vindo(a), {original_db_name}!")
                return row
    
    st.error("⚠️ Nome não encontrado na lista de convidados.")
    return None

def save_registration(participant_data, visitors_data):
    """Save registration to CSV file."""
    # Create data directory if it doesn't exist
    os.makedirs('./data', exist_ok=True)
    
    registration_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Prepare rows for each visitor
    rows = []
    for i, visitor in enumerate(visitors_data):
        row = {
            'registration_id': registration_id,
            'timestamp': timestamp,
            'invitee_name': participant_data['full_name'],
            'invitee_id': participant_data.get('id', ''),
            'visitor_number': i + 1,
            'visitor_name': visitor['name'],
            'visitor_rg': visitor['rg'],
            'is_primary': i == 0  # First visitor is the invitee
        }
        rows.append(row)
    
    # Check if file exists
    file_path = './data/RESULTADOS.CSV'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    else:
        df = pd.DataFrame(rows)
    
    df.to_csv(file_path, index=False)
    
    return registration_id

def show_participant_count_form():
    """Show form to get number of participants when participants field is 0."""
    participant = st.session_state.participant_data
    
    st.markdown(f"### Olá, {participant['full_name']}! 👋")
    st.markdown("### 👥 Quantos acompanhantes você levará?")
    
    companions = st.number_input(
        "Número de acompanhantes (não incluindo você):",
        min_value=0,
        max_value=MAX_COMPANIONS,
        value=0,
        help="Informe quantas pessoas irão com você, além de você mesmo(a)."
    )
    
    total = companions + 1  # Add 1 for the invitee
    st.info(f"Total de visitantes: {total} pessoa(s)")
    
    if st.button("Continuar para Registro", type="primary"):
        st.session_state.total_participants = total
        st.session_state.show_registration = True
        st.rerun()

def show_registration_form():
    """Show the visitor registration form."""
    participant = st.session_state.participant_data
    total_participants = st.session_state.total_participants
    
    st.markdown(f"### 📋 Registro de Visitantes")
    st.markdown(f"**Convidado:** {participant['full_name']}")
    st.markdown(f"**Total de visitantes:** {total_participants}")
    st.markdown("---")
    
    visitors_data = []
    all_valid = True
    
    # For each participant, collect name and RG
    for i in range(total_participants):
        st.markdown(f"#### Visitante {i + 1}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # First visitor is the invitee
            if i == 0:
                name = participant['full_name']
                st.text_input("Nome completo:", value=name, disabled=True, key=f"name_{i}")
            else:
                name = st.text_input("Nome completo:", key=f"name_{i}")
        
        with col2:
            rg = st.text_input("RG:", key=f"rg_{i}", help="Digite apenas números")
        
        # Validate inputs
        if i == 0:
            name = participant['full_name']  # Ensure we use the correct name
        
        if name and rg:
            # Clean RG (remove non-numeric characters)
            rg_clean = re.sub(r'[^0-9]', '', rg)
            if rg_clean:
                visitors_data.append({
                    'name': name.strip(),
                    'rg': rg_clean
                })
            else:
                all_valid = False
                st.error(f"❌ RG do visitante {i + 1} deve conter números")
        else:
            all_valid = False
            if not name and i > 0:
                st.error(f"❌ Nome do visitante {i + 1} é obrigatório")
            if not rg:
                st.error(f"❌ RG do visitante {i + 1} é obrigatório")
    
    st.markdown("---")
    
    # Submit button
    if st.button("Confirmar Registro", type="primary", disabled=not all_valid):
        if len(visitors_data) == total_participants:
            # Save registration
            registration_id = save_registration(participant, visitors_data)
            
            # Show success message
            st.success(f"✅ Registro confirmado! ID: {registration_id}")
            st.markdown(MESSAGES['registration_success'])
            
            # Show registered visitors
            st.markdown("### 👥 Visitantes Registrados:")
            for i, visitor in enumerate(visitors_data):
                st.markdown(f"{i + 1}. **{visitor['name']}** - RG: {visitor['rg']}")
            
            # New registration button
            if st.button("Novo Registro", type="secondary"):
                # Reset session state
                for key in ['confirmed', 'participant_data', 'show_registration', 
                           'total_participants', 'visitors_data']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

def main():
    """Main application flow."""
    # Custom CSS
    st.markdown("""
    <style>
    .event-title {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1e3a8a !important;
        margin-bottom: 0.5rem !important;
        line-height: 1.2 !important;
    }
    @media (max-width: 768px) {
        .event-title {
            font-size: 1.5rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display title
    st.markdown(f'<h1 class="event-title">🏛️ {EVENT_NAME}</h1>', unsafe_allow_html=True)
    
    st.markdown(f"📅 **Data:** {EVENT_DATE}")
    st.markdown(f"📍 **Local:** {EVENT_LOCATION}")
    st.markdown("---")
    
    # Load participants
    participants_df = load_participants()
    
    if participants_df.empty:
        st.error("Lista de participantes vazia ou não carregada")
        return
    
    # Check which page to show
    if st.session_state.show_registration:
        show_registration_form()
    elif not st.session_state.confirmed:
        # Step 1: Name verification
        st.markdown("### 👤 Verificação de Convidado")
        
        name_input = st.text_input("Digite seu nome completo:", 
                                   placeholder="Ex: João da Silva")
        
        if st.button("Verificar", type="primary"):
            if name_input:
                participant = find_participant(name_input, participants_df)
                
                if participant is not None:
                    st.session_state.participant_data = participant
                    st.session_state.confirmed = True
                    
                    # Check participants count
                    participants_count = int(participant.get('participants', 0))
                    
                    if participants_count == 0:
                        # Need to ask for number of companions
                        st.rerun()
                    else:
                        # Use the predefined count
                        st.session_state.total_participants = participants_count
                        st.session_state.show_registration = True
                        st.rerun()
            else:
                st.warning("Por favor, digite seu nome.")
    else:
        # Step 2: Get participant count if needed
        participant = st.session_state.participant_data
        participants_count = int(participant.get('participants', 0))
        
        if participants_count == 0:
            show_participant_count_form()
        else:
            # Use predefined count and go directly to registration
            st.session_state.total_participants = participants_count
            st.session_state.show_registration = True
            st.rerun()

def admin_panel():
    """Admin panel for viewing registrations."""
    st.title("🔐 Painel Administrativo - Registros DCTA")
    
    password = st.text_input("Senha:", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("Acesso autorizado!")
        
        # Load registrations
        try:
            df = pd.read_csv('./data/RESULTADOS.CSV')
            
            # Statistics
            st.markdown("### 📊 Estatísticas")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                unique_registrations = df['registration_id'].nunique()
                st.metric("Registros Únicos", unique_registrations)
            
            with col2:
                total_visitors = len(df)
                st.metric("Total de Visitantes", total_visitors)
            
            with col3:
                unique_invitees = df['invitee_name'].nunique()
                st.metric("Convidados Únicos", unique_invitees)
            
            with col4:
                avg_group_size = df.groupby('registration_id').size().mean()
                st.metric("Tamanho Médio do Grupo", f"{avg_group_size:.1f}")
            
            # Registrations table
            st.markdown("### 📋 Lista de Registros")
            
            # Allow filtering by invitee
            invitee_filter = st.selectbox(
                "Filtrar por convidado:",
                ["Todos"] + sorted(df['invitee_name'].unique().tolist())
            )
            
            if invitee_filter != "Todos":
                filtered_df = df[df['invitee_name'] == invitee_filter]
            else:
                filtered_df = df
            
            st.dataframe(filtered_df.sort_values('timestamp', ascending=False))
            
            # Export option
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name=f"registros_dcta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        except FileNotFoundError:
            st.info("Nenhum registro encontrado ainda.")
    
    elif password:
        st.error("Senha incorreta!")

# Run the app
if __name__ == "__main__":
    # Check if admin mode
    query_params = st.query_params
    
    if 'admin' in query_params:
        admin_panel()
    else:
        main()