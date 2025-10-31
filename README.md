#  Análise de Aderência de Perfis do LinkedIn

Sistema inteligente para análise automática de perfis do LinkedIn® e cálculo de aderência a vagas de emprego.

## Funcionalidades

- ✅ **Interface Web Interativa**: Criada com Streamlit para fácil uso
- ✅ **Descrição Detalhada de Vagas**: Configure todos os requisitos da vaga
- ✅ **Análise Automática de Perfis**: Processa todos os perfis do dataset
- ✅ **Sistema de Pontuação Inteligente**: Algoritmo multi-critério com 5 dimensões de análise
- ✅ **Top 5 Perfis**: Ranking dos candidatos mais aderentes
- ✅ **Justificativas Detalhadas**: Explicação clara do motivo de cada classificação
- ✅ **Visualizações Interativas**: Gráficos e métricas visuais
- ✅ **Exportação de Resultados**: Download em JSON e CSV
##Como Usar

### 1. Instalação e execução

```bash

run.ps1
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

### 2. Configurar a Vaga

Na barra lateral esquerda, preencha:

- **Título da Vaga**: Nome da posição
- **Grau de Escolaridade**: Nível mínimo exigido
- **Conhecimentos Desejados**: Habilidades desejadas (separadas por vírgula)
- **Conhecimentos Obrigatórios**: Habilidades essenciais (separadas por vírgula)
- **Tempo de Experiência**: Anos mínimos de experiência
- **Outras Observações**: Requisitos adicionais ou contexto da vaga

### 3. Carregar Dataset de Perfis

Vá para a aba **"Dataset"**:

- **Opção 1**: Use o dataset de exemplo (`perfis_example.json`)
- **Opção 2**: Faça upload do seu próprio arquivo CSV ou JSON

- Análise detalhada de cada perfil
- Breakdown da pontuação por critério
- Lista completa de todos os perfis classificados

## Sistema de Pontuação

### a. Escolaridade (até 15 pontos)
- Verifica se o candidato possui o grau mínimo exigido
- Pontuação completa se atende ao requisito

- 10 pontos por habilidade obrigatória encontrada
- Máximo de 30 pontos (3 habilidades)
- Match inteligente (considera variações)

### b. Conhecimentos Desejados (até 10 pontos)
- 2 pontos por habilidade desejada encontrada

### c. Similaridade Textual (até 30 pontos)
- Identifica compatibilidade de contexto e linguagem


```json
}
    "nome": "Nome do Candidato",
    "habilidades": "Python, SQL, Machine Learning",
}
```

**Campos obrigatórios:**
- `url`: Link do perfil LinkedIn
- `nome`: Nome completo do candidato
- `habilidades`: Lista de habilidades separadas por vírgula
- `educacao`: Um dos valores: `Fundamental`, `Médio`, `Superior`, `Pós-graduação`, `Mestrado`, `Doutorado`
- `experiencia_anos`: Número inteiro de anos de experiência
- `resumo`: Texto descritivo do perfil profissional

### Exemplo de CSV

```csv
url,nome,habilidades,educacao,experiencia_anos,resumo
https://www.linkedin.com/in/exemplo,João Silva,"Python, SQL, Machine Learning",Superior,3,Cientista de dados com experiência em projetos reais
```

- `requirements.txt` — Dependências do projeto
- `README.md` — Documentação

## Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/)** — Framework para interface web
- **[Pandas](https://pandas.pydata.org/)** — Manipulação de dados
- **[Scikit-learn](https://scikit-learn.org/)** — TF-IDF e análise de similaridade
- **[Plotly](https://plotly.com/)** — Visualizações interativas


### Vaga para Analista de BI
- Obrigatórios: SQL, Power BI
- Desejados: Excel, Tableau
- Experiência: 3 anos
