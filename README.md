# Programa de Feedback Estudantil

Aplicação web desenvolvida como parte da **Atividade Extensionista II — Tecnologia Aplicada à Inclusão Digital**, do curso de **CST em Análise e Desenvolvimento de Sistemas**.

## Sobre o Projeto

O Programa de Feedback Estudantil é uma plataforma web que promove a comunicação construtiva entre alunos e professores. Através de avaliações anônimas, os alunos podem destacar pontos positivos e sugerir melhorias, enquanto os professores têm acesso a um painel com as médias e comentários recebidos.

**Setor de Aplicação:** Instituições de ensino em Vitória da Conquista - BA  
**ODS:** 4 — Educação de Qualidade

### Autores
- Leonardo Ribeiro Souza (RU 5223563)
- Gregory Antunes Hack (RU 3699000)

## Tecnologias Utilizadas

- **Python 3** — Linguagem de programação
- **Flask** — Framework web
- **SQLite** — Banco de dados
- **HTML5 / CSS3 / JavaScript** — Interface do usuário

## Funcionalidades

1. **Avaliação Anônima** — Alunos avaliam professores em 4 critérios (Didática, Pontualidade, Domínio do Conteúdo, Relacionamento com Alunos), com notas de 1 a 5 estrelas.
2. **Comentários Construtivos** — Campos separados para pontos positivos e aspectos a melhorar.
3. **Dashboard do Professor** — Painel com médias por critério, gráfico de barras e listagem de comentários anônimos.
4. **Interface Responsiva** — Funciona em computadores e dispositivos móveis.

## Como Executar

### Pré-requisitos

- Python 3.8 ou superior instalado

### Passo a Passo

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Criar e popular o banco de dados:**
   ```bash
   python init_db.py
   ```

3. **Iniciar o servidor:**
   ```bash
   python app.py
   ```

4. **Acessar no navegador:**
   ```
   http://127.0.0.1:5000
   ```

### Códigos de Acesso dos Professores (dados de exemplo)

| Professor                   | Código de Acesso |
|-----------------------------|------------------|
| Prof. Ana Maria Silva       | ana123           |
| Prof. Carlos Eduardo Santos | carlos123        |
| Prof. Fernanda Oliveira     | fernanda123      |
| Prof. João Pedro Lima       | joao123          |
| Prof. Maria Clara Souza     | maria123         |

## Estrutura do Projeto

```
Extensionista/
├── app.py                 # Servidor Flask (aplicação principal)
├── init_db.py             # Script de criação do banco de dados
├── requirements.txt       # Dependências do projeto
├── feedback.db            # Banco de dados SQLite (gerado após init_db.py)
├── README.md              # Este arquivo
├── static/
│   └── style.css          # Estilos da interface
└── templates/
    ├── base.html           # Template base (layout comum)
    ├── index.html          # Página inicial
    ├── avaliar.html        # Formulário de avaliação do aluno
    ├── login_professor.html# Login do professor
    ├── dashboard.html      # Painel do professor
    └── sucesso.html        # Confirmação de envio
```

## Licença

Projeto acadêmico desenvolvido para fins educacionais.
