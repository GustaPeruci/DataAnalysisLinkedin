import streamlit as st
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).parent

st.title('Análise de Aderência de Perfis do LinkedIn à Vaga')

st.header('Descrição da Vaga')
grau_escolaridade = st.selectbox('Grau de escolaridade', ['Fundamental', 'Médio', 'Superior', 'Pós-graduação', 'Mestrado', 'Doutorado'])
conhecimentos_desejados = st.text_area('Conhecimentos desejados (separados por vírgula)')
conhecimentos_obrigatorios = st.text_area('Conhecimentos obrigatórios (separados por vírgula)')
tempo_experiencia = st.number_input('Tempo de experiência (anos)', min_value=0, max_value=50, value=1)
outras_observacoes = st.text_area('Outras observações')

def vaga_to_dict() -> Dict[str, Any]:
    return {
        'grau_escolaridade': grau_escolaridade,
        'conhecimentos_desejados': [s.strip() for s in conhecimentos_desejados.split(',') if s.strip()],
        'conhecimentos_obrigatorios': [s.strip() for s in conhecimentos_obrigatorios.split(',') if s.strip()],
        'tempo_experiencia': int(tempo_experiencia),
        'outras_observacoes': outras_observacoes,
    }

if st.button('Salvar vaga (salva em vaga.json)'):
    vaga = vaga_to_dict()
    with open(ROOT / 'vaga.json', 'w', encoding='utf-8') as f:
        json.dump(vaga, f, ensure_ascii=False, indent=2)
    st.success('Vaga salva em vaga.json')

st.header('Dataset de Perfis')
dataset_file = st.file_uploader('Envie o arquivo CSV ou JSON com os perfis estruturados (campos: url, nome, habilidades, educacao, experiencia_anos, resumo)', type=['csv','json'])

use_example = st.checkbox('Carregar dataset de exemplo (perfis_example.json)', value=True)

def load_profiles(file) -> List[Dict[str, Any]]:
    if not file:
        return []
    if isinstance(file, (str, Path)):
        p = Path(file)
        if p.suffix == '.json':
            return json.loads(p.read_text(encoding='utf-8'))
        else:
            return pd.read_csv(p).to_dict(orient='records')
    # Uploaded file-like
    if hasattr(file, 'read'):
        content = file.read()
        try:
            return json.loads(content)
        except Exception:
            file.seek(0)
            return pd.read_csv(file).to_dict(orient='records')
    return []

profiles: List[Dict[str, Any]] = []
if dataset_file:
    profiles = load_profiles(dataset_file)
elif use_example:
    example_path = ROOT / 'perfis_example.json'
    if example_path.exists():
        profiles = load_profiles(str(example_path))
    else:
        st.warning('Dataset de exemplo não encontrado. Você pode enviar um arquivo CSV/JSON.')

if profiles:
    df = pd.DataFrame(profiles)
    st.write('Perfis carregados:', df)

    # Pontuação simples
    escolaridade_rank = {
        'Fundamental': 0,
        'Médio': 1,
        'Superior': 2,
        'Pós-graduação': 3,
        'Mestrado': 4,
        'Doutorado': 5,
    }

    def score_profile(profile: Dict[str, Any], vaga: Dict[str, Any], tfidf_vectorizer: TfidfVectorizer, vaga_vec) -> Dict[str, Any]:
        score = 0
        reasons: List[str] = []

        # Escolaridade
        perfil_edu = profile.get('educacao', '')
        perfil_rank = escolaridade_rank.get(perfil_edu, 0)
        vaga_rank = escolaridade_rank.get(vaga['grau_escolaridade'], 0)
        if perfil_rank >= vaga_rank:
            score += 15
            reasons.append('Escolaridade atende à exigida')
        else:
            reasons.append('Escolaridade abaixo do exigido')

        # Experiência
        exp = int(profile.get('experiencia_anos') or 0)
        if exp >= vaga['tempo_experiencia']:
            score += 15
            reasons.append(f'Experiência: {exp} anos >= {vaga["tempo_experiencia"]} anos')
        else:
            reasons.append(f'Experiência: {exp} anos < {vaga["tempo_experiencia"]} anos')

        # Habilidades obrigatórias (match exato)
        perfil_skills = [s.strip().lower() for s in profile.get('habilidades','').split(',') if s.strip()] if profile.get('habilidades') else []
        obrig = [s.strip().lower() for s in vaga['conhecimentos_obrigatorios']]
        desej = [s.strip().lower() for s in vaga['conhecimentos_desejados']]

        if obrig:
            matched_obrig = [s for s in obrig if s in perfil_skills]
            obrig_score = min(30, len(matched_obrig) * 10)
            score += obrig_score
            if matched_obrig:
                reasons.append(f'Habilidades obrigatórias encontradas: {", ".join(matched_obrig)}')
            else:
                reasons.append('Nenhuma habilidade obrigatória encontrada')

        # Habilidades desejadas (match exato)
        if desej:
            matched_desej = [s for s in desej if s in perfil_skills]
            desej_score = min(10, len(matched_desej) * 2)
            score += desej_score
            if matched_desej:
                reasons.append(f'Habilidades desejadas encontradas: {", ".join(matched_desej)}')

        # Similaridade textual (TF-IDF) entre vaga (descrição + skills) e perfil (resumo + habilidades)
        perfil_text = ' '.join([profile.get('resumo',''), profile.get('habilidades','')])
        perfil_vec = tfidf_vectorizer.transform([perfil_text])
        sim = float(cosine_similarity(vaga_vec, perfil_vec)[0][0])
        sim_score = int(sim * 30)  # até 30 pontos
        score += sim_score
        reasons.append(f'Similaridade texto {sim:.2f} -> +{sim_score} pontos')

        # normalize to percentage-ish scale (max around 100)
        score = min(100, score)
        return {'score': score, 'reasons': reasons}

    vaga = vaga_to_dict()
    # preparar TF-IDF
    corpus = [vaga['outras_observacoes'] + ' ' + ' '.join(vaga['conhecimentos_desejados'] + vaga['conhecimentos_obrigatorios'])]
    # adicionar resumos dos perfis ao corpus para treino do vocabulário
    for p in profiles:
        corpus.append((p.get('resumo','') or '') + ' ' + (p.get('habilidades','') or ''))
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(corpus)
    vaga_vec = tfidf_matrix[0]

    scored = []
    for idx, p in enumerate(profiles, start=1):
        res = score_profile(p, vaga, tfidf, vaga_vec)
        scored.append({**p, **res})

    scored_sorted = sorted(scored, key=lambda x: x['score'], reverse=True)

    st.header('Top 5 perfis')
    for i, s in enumerate(scored_sorted[:5], start=1):
        st.subheader(f'{i}. {s.get("nome") or s.get("url")} — {s["score"]}%')
        st.write('Motivos:')
        for r in s['reasons']:
            st.write('- ' + r)

else:
    st.info('Nenhum perfil carregado ainda.')
