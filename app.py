import streamlit as st
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).parent

# Configuração da página
st.set_page_config(
    page_title="Análise de Aderência de Perfis",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Análise de Aderência de Perfis do LinkedIn")

# Sidebar para configuração da vaga
with st.sidebar:
    st.header('Descrição da Vaga')
    
    titulo_vaga = st.text_input('Título da Vaga', value='Cientista de Dados')
    
    grau_escolaridade = st.selectbox(
        'Grau de Escolaridade Mínimo', 
        ['Fundamental', 'Médio', 'Superior', 'Pós-graduação', 'Mestrado', 'Doutorado'],
        index=2
    )
    
    conhecimentos_desejados = st.text_area(
        'Conhecimentos Desejados (separados por vírgula)',
        value='Python, Machine Learning, SQL'
    )
    
    conhecimentos_obrigatorios = st.text_area(
        'Conhecimentos Obrigatórios (separados por vírgula)',
        value='Python, Estatística'
    )
    
    tempo_experiencia = st.number_input(
        'Tempo de Experiência Mínimo (anos)', 
        min_value=0, 
        max_value=50, 
        value=2
    )
    
    outras_observacoes = st.text_area(
        'Outras Observações',
        value='Experiência com projetos reais em ciência de dados'
    )

    if st.button('Salvar Vaga'):
        vaga = {
            'titulo': titulo_vaga,
            'grau_escolaridade': grau_escolaridade,
            'conhecimentos_desejados': [s.strip() for s in conhecimentos_desejados.split(',') if s.strip()],
            'conhecimentos_obrigatorios': [s.strip() for s in conhecimentos_obrigatorios.split(',') if s.strip()],
            'tempo_experiencia': int(tempo_experiencia),
            'outras_observacoes': outras_observacoes,
        }
        with open(ROOT / 'vaga.json', 'w', encoding='utf-8') as f:
            json.dump(vaga, f, ensure_ascii=False, indent=2)
        st.success('✅ Vaga salva com sucesso!')
    
    st.write("")
    # Carregar vaga salva
    if st.button('Carregar Vaga Salva'):
        vaga_path = ROOT / 'vaga.json'
        if vaga_path.exists():
            st.info('Vaga carregada do arquivo vaga.json')
        else:
            st.warning('Nenhuma vaga salva encontrada')

def vaga_to_dict() -> Dict[str, Any]:
    return {
        'titulo': titulo_vaga,
        'grau_escolaridade': grau_escolaridade,
        'conhecimentos_desejados': [s.strip() for s in conhecimentos_desejados.split(',') if s.strip()],
        'conhecimentos_obrigatorios': [s.strip() for s in conhecimentos_obrigatorios.split(',') if s.strip()],
        'tempo_experiencia': int(tempo_experiencia),
        'outras_observacoes': outras_observacoes,
    }

# Área principal
tab1, tab2, tab3 = st.tabs(["Análise de Perfis", "Dataset", "Informações"])

with tab2:
    st.header('Dataset de Perfis')
    
    col1, col2 = st.columns(2)
    
    with col1:
        dataset_file = st.file_uploader(
            'Envie o arquivo CSV ou JSON com os perfis',
            type=['csv','json'],
            help='O arquivo deve conter: url, nome, habilidades, educacao, experiencia_anos, resumo'
        )
    
    with col2:
        use_example = st.checkbox('Usar dataset de exemplo (perfis_example.json)', value=True)
        if st.button('Ver formato esperado'):
            st.json({
                "url": "https://www.linkedin.com/in/exemplo",
                "nome": "Nome do Candidato",
                "habilidades": "Python, SQL, Machine Learning",
                "educacao": "Superior",
                "experiencia_anos": 3,
                "resumo": "Breve descrição profissional"
            })

with tab3:
     st.header('Como Funciona')
     st.markdown("""
     **Sistema de Pontuação**
    
     O algoritmo analisa cada perfil com base nos seguintes critérios:
    
     1. Escolaridade (até 15 pontos)
     2. Experiência (até 15 pontos)
     3. Conhecimentos obrigatórios (até 30 pontos)
     4. Conhecimentos desejados (até 10 pontos)
     5. Similaridade textual (até 30 pontos)
    
     Pontuação máxima: 100 pontos
    
     **Formato dos Dados**
     Perfis em CSV ou JSON com os campos:
     - url: Link do perfil LinkedIn
     - nome: Nome completo
     - habilidades: Habilidades separadas por vírgula
     - educacao: Nível de escolaridade
     - experiencia_anos: Anos de experiência
     - resumo: Resumo profissional
     """)

def load_profiles(file) -> List[Dict[str, Any]]:
    """Carrega perfis de um arquivo CSV ou JSON"""
    if not file:
        return []
    if isinstance(file, (str, Path)):
        p = Path(file)
        if p.suffix == '.json':
            return json.loads(p.read_text(encoding='utf-8'))
        else:
            df = pd.read_csv(p)
            # Converter NaN para strings vazias
            df = df.fillna('')
            return df.to_dict(orient='records')
    # Uploaded file-like
    if hasattr(file, 'read'):
        content = file.read()
        try:
            return json.loads(content)
        except Exception:
            file.seek(0)
            df = pd.read_csv(file)
            df = df.fillna('')
            return df.to_dict(orient='records')
    return []

# Ranking de escolaridade
escolaridade_rank = {
    'Fundamental': 0,
    'Médio': 1,
    'Superior': 2,
    'Pós-graduação': 3,
    'Mestrado': 4,
    'Doutorado': 5,
}

def score_profile(profile: Dict[str, Any], vaga: Dict[str, Any], tfidf_vectorizer: TfidfVectorizer, vaga_vec) -> Dict[str, Any]:
    """Calcula a pontuação de aderência de um perfil à vaga"""
    score = 0
    reasons: List[str] = []
    details = {
        'escolaridade': 0,
        'experiencia': 0,
        'obrigatorios': 0,
        'desejados': 0,
        'similaridade': 0
    }

    # 1. Escolaridade (até 15 pontos)
    perfil_edu = profile.get('educacao', '')
    perfil_rank = escolaridade_rank.get(perfil_edu, 0)
    vaga_rank = escolaridade_rank.get(vaga['grau_escolaridade'], 0)
    if perfil_rank >= vaga_rank:
        edu_score = 15
        score += edu_score
        details['escolaridade'] = edu_score
        reasons.append(f'Escolaridade: {perfil_edu} (mínimo exigido: {vaga["grau_escolaridade"]})')
    else:
        reasons.append(f'Escolaridade: {perfil_edu} (abaixo do mínimo exigido: {vaga["grau_escolaridade"]})')

    # 2. Experiência (até 15 pontos)
    exp = int(profile.get('experiencia_anos') or 0)
    exp_req = vaga['tempo_experiencia']
    if exp >= exp_req:
        exp_score = 15
        score += exp_score
        details['experiencia'] = exp_score
        reasons.append(f'Experiência: {exp} anos (mínimo exigido: {exp_req} anos)')
    else:
        exp_diff = exp_req - exp
        reasons.append(f'Experiência: {exp} anos (faltam {exp_diff} anos para o mínimo de {exp_req})')

    # 3. Habilidades obrigatórias (até 30 pontos)
    perfil_skills = [s.strip().lower() for s in profile.get('habilidades','').split(',') if s.strip()] if profile.get('habilidades') else []
    obrig = [s.strip().lower() for s in vaga['conhecimentos_obrigatorios']]
    
    if obrig:
        matched_obrig = [s for s in obrig if any(s in skill or skill in s for skill in perfil_skills)]
        missing_obrig = [s for s in obrig if not any(s in skill or skill in s for skill in perfil_skills)]
        
        # 10 pontos por habilidade obrigatória, máximo 30
        obrig_score = min(30, len(matched_obrig) * 10)
        score += obrig_score
        details['obrigatorios'] = obrig_score
        
        if matched_obrig:
            reasons.append(f'Conhecimentos obrigatórios atendidos ({len(matched_obrig)}/{len(obrig)}): {", ".join(matched_obrig)}')
        if missing_obrig:
            reasons.append(f'Conhecimentos obrigatórios faltantes: {", ".join(missing_obrig)}')
    else:
        reasons.append('Nenhum conhecimento obrigatório especificado')

    # 4. Habilidades desejadas (até 10 pontos)
    desej = [s.strip().lower() for s in vaga['conhecimentos_desejados']]
    if desej:
        matched_desej = [s for s in desej if any(s in skill or skill in s for skill in perfil_skills)]
        # 2 pontos por habilidade desejada, máximo 10
        desej_score = min(10, len(matched_desej) * 2)
        score += desej_score
        details['desejados'] = desej_score
        
        if matched_desej:
            reasons.append(f'Conhecimentos desejados encontrados ({len(matched_desej)}/{len(desej)}): {", ".join(matched_desej)}')
        else:
            reasons.append(f'Nenhum conhecimento desejado encontrado')

    # 5. Similaridade textual (até 30 pontos)
    try:
        perfil_text = ' '.join([str(profile.get('resumo','')), str(profile.get('habilidades',''))])
        if perfil_text.strip():
            perfil_vec = tfidf_vectorizer.transform([perfil_text])
            sim = float(cosine_similarity(vaga_vec, perfil_vec)[0][0])
            sim_score = int(sim * 30)  # até 30 pontos
            score += sim_score
            details['similaridade'] = sim_score
            reasons.append(f'Similaridade textual: {sim:.2%}')
        else:
            reasons.append('Sem resumo/texto para análise de similaridade')
    except Exception as e:
        reasons.append(f'Erro na análise de similaridade: {str(e)}')

    # Normalizar pontuação (máximo 100)
    score = min(100, score)
    
    return {
        'score': score, 
        'reasons': reasons,
        'details': details
    }

# Carregar perfis
profiles: List[Dict[str, Any]] = []
with tab1:
    if dataset_file:
        profiles = load_profiles(dataset_file)
        st.success(f'✅ {len(profiles)} perfis carregados do arquivo enviado')
    elif use_example:
        example_path = ROOT / 'perfis_example.json'
        if example_path.exists():
            profiles = load_profiles(str(example_path))
            st.info(f'📂 {len(profiles)} perfis carregados do dataset de exemplo')
        else:
            st.warning('⚠️ Dataset de exemplo não encontrado. Envie um arquivo CSV/JSON na aba Dataset.')

if profiles:
    with tab2:
        st.subheader('Visualização dos Perfis Carregados')
        df_display = pd.DataFrame(profiles)
        st.dataframe(df_display, use_container_width=True)
        
        # Estatísticas do dataset
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Perfis", len(profiles))
        with col2:
            if 'experiencia_anos' in df_display.columns:
                avg_exp = df_display['experiencia_anos'].mean()
                st.metric("Experiência Média", f"{avg_exp:.1f} anos")
        with col3:
            if 'educacao' in df_display.columns:
                most_common_edu = df_display['educacao'].mode()[0] if not df_display['educacao'].empty else 'N/A'
                st.metric("Escolaridade Mais Comum", most_common_edu)

        with tab1:
            st.header('Análise de Aderência')
            vaga = vaga_to_dict()
            # Preparar TF-IDF
            with st.spinner('Processando perfis...'):
                corpus = [vaga['outras_observacoes'] + ' ' + ' '.join(vaga['conhecimentos_desejados'] + vaga['conhecimentos_obrigatorios'])]
                for p in profiles:
                    text = str(p.get('resumo','') or '') + ' ' + str(p.get('habilidades','') or '')
                    corpus.append(text)
                tfidf = TfidfVectorizer(stop_words='english', max_features=100)
                tfidf_matrix = tfidf.fit_transform(corpus)
                vaga_vec = tfidf_matrix[0]
                scored = []
                for idx, p in enumerate(profiles, start=1):
                    res = score_profile(p, vaga, tfidf, vaga_vec)
                    scored.append({**p, **res})
                scored_sorted = sorted(scored, key=lambda x: x['score'], reverse=True)
            st.success(f'{len(profiles)} perfis analisados com sucesso!')
            with st.expander("Resumo da Vaga", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Título: {vaga['titulo']}")
                    st.write(f"Escolaridade mínima: {vaga['grau_escolaridade']}")
                    st.write(f"Experiência mínima: {vaga['tempo_experiencia']} anos")
                with col2:
                    st.write(f"Conhecimentos obrigatórios: {', '.join(vaga['conhecimentos_obrigatorios'])}")
                    st.write(f"Conhecimentos desejados: {', '.join(vaga['conhecimentos_desejados'])}")
                st.write(f"Observações: {vaga['outras_observacoes']}")
            st.subheader('Distribuição de Pontuações')
            scores_df = pd.DataFrame(scored_sorted)
            fig = px.histogram(
                scores_df, 
                x='score', 
                nbins=20,
                labels={'score': 'Pontuação de Aderência', 'count': 'Número de Perfis'},
                title='Distribuição de Pontuações dos Candidatos'
            )
            fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True, key="histogram_scores")
        st.header('Top 5 Perfis Mais Aderentes')
        for i, s in enumerate(scored_sorted[:5], start=1):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"{i}º - {s.get('nome', 'Nome não informado')}")
                with col2:
                    st.metric("Pontuação", f"{s['score']}%")
                with col3:
                    if s.get('url'):
                        st.markdown(f"[Ver Perfil]({s['url']})")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"Escolaridade: {s.get('educacao', 'N/A')}")
                with col2:
                    st.write(f"Experiência: {s.get('experiencia_anos', 0)} anos")
                with col3:
                    st.write(f"Habilidades: {s.get('habilidades', 'N/A')}")
                details = s.get('details', {})
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Escolaridade', 'Experiência', 'Obrigatórios', 'Desejados', 'Similaridade'],
                        y=[details.get('escolaridade', 0), details.get('experiencia', 0), 
                           details.get('obrigatorios', 0), details.get('desejados', 0), 
                           details.get('similaridade', 0)],
                        marker_color=['#888', '#888', '#888', '#888', '#888']
                    )
                ])
                fig.update_layout(
                    title='Pontuação por Critério',
                    yaxis_title='Pontos',
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True, key=f"breakdown_{i}")
                st.markdown("Análise Detalhada:")
                for r in s['reasons']:
                    st.markdown(f"- {r}")
                if s.get('resumo'):
                    with st.expander("Resumo Profissional"):
                        st.write(s['resumo'])
                st.write("")
        with st.expander(f"Ver Todos os {len(scored_sorted)} Perfis Classificados"):
            for idx, profile in enumerate(scored_sorted, 1):
                col1, col2, col3 = st.columns([1, 4, 1])
                with col1:
                    st.write(f"{idx}º")
                with col2:
                    st.write(f"{profile.get('nome', 'N/A')}")
                with col3:
                    st.write(f"{profile['score']}%")
        st.subheader('Exportar Resultados')
        col1, col2 = st.columns(2)
        with col1:
            result_json = json.dumps(scored_sorted[:5], ensure_ascii=False, indent=2)
            st.download_button(
                label="Download Top 5 (JSON)",
                data=result_json,
                file_name="top5_perfis.json",
                mime="application/json"
            )
        with col2:
            result_df = pd.DataFrame(scored_sorted[:5])
            csv = result_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="Download Top 5 (CSV)",
                data=csv,
                file_name="top5_perfis.csv",
                mime="text/csv"
            )

else:
    with tab1:
        st.info('Carregue um dataset de perfis na aba "Dataset" para começar a análise')
        st.markdown("""
        Como começar:
        1. Configure a vaga na barra lateral esquerda
        2. Vá para a aba "Dataset" 
        3. Envie um arquivo CSV/JSON ou use o dataset de exemplo
        4. Volte para esta aba para ver a análise completa
        """)
