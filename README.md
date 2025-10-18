# Análise de Aderência de Perfis ao Vaga (LinkedIn)

Este projeto fornece uma interface Streamlit para descrever uma vaga e pontuar perfis do LinkedIn armazenados localmente (CSV/JSON).

Arquivos principais:
- `app.py` — Aplicação Streamlit.
- `perfis_example.json` — Dataset de exemplo com perfis estruturados.
- `vaga.json` — (gerado) arquivo que contém a última vaga salva.

Formato esperado para perfis (CSV/JSON):
- url: link do perfil (string)
- nome: nome do candidato (string)
- habilidades: lista/CSV de habilidades no campo como string, ex: "Python, SQL, Machine Learning"
- educacao: uma das tags: Fundamental, Médio, Superior, Pós-graduação, Mestrado, Doutorado
- experiencia_anos: número inteiro com anos de experiência
- resumo: texto livre (opcional)

Instruções rápidas:
1. Instale dependências: `pip install -r requirements.txt`
2. Rode a aplicação: `streamlit run app.py`
3. Preencha a descrição da vaga e clique em "Salvar vaga" para gerar `vaga.json`.
4. Faça upload do seu dataset (CSV/JSON) ou deixe marcado para usar o dataset de exemplo.