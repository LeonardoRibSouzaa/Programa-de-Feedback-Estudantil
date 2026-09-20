"""
Programa de Feedback Estudantil
Atividade Extensionista II - Tecnologia Aplicada à Inclusão Digital

Aplicação web que permite alunos avaliarem professores de forma anônima,
promovendo a comunicação construtiva entre alunos e professores.

Autores: Leonardo Ribeiro Souza (RU 5223563), Gregory Antunes Hack (RU 3699000)
Curso: CST em Análise e Desenvolvimento de Sistemas
Setor de Aplicação: Instituições de ensino em Vitória da Conquista - BA
ODS 4: Educação de Qualidade
"""

import json
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'feedback-estudantil-extensionista-2026'

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feedback.db')


def get_db():
    """Retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==================== ROTAS PRINCIPAIS ====================

@app.route('/')
def index():
    """Página inicial."""
    return render_template('index.html')


@app.route('/aluno/avaliar', methods=['GET', 'POST'])
def avaliar():
    """Formulário de avaliação (GET) e processamento (POST)."""
    db = get_db()

    if request.method == 'POST':
        try:
            professor_id = int(request.form['professor_id'])
            disciplina_id = int(request.form['disciplina_id'])
            didatica = int(request.form['didatica'])
            pontualidade = int(request.form['pontualidade'])
            dominio_conteudo = int(request.form['dominio_conteudo'])
            relacionamento = int(request.form['relacionamento'])
            pontos_positivos = request.form.get('pontos_positivos', '').strip()
            aspectos_melhorar = request.form.get('aspectos_melhorar', '').strip()

            # Validar notas entre 1 e 5
            for nota in [didatica, pontualidade, dominio_conteudo, relacionamento]:
                if nota < 1 or nota > 5:
                    flash('As notas devem estar entre 1 e 5.', 'error')
                    return redirect(url_for('avaliar'))

            db.execute(
                '''INSERT INTO avaliacoes
                   (professor_id, disciplina_id, didatica, pontualidade,
                    dominio_conteudo, relacionamento, pontos_positivos, aspectos_melhorar)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (professor_id, disciplina_id, didatica, pontualidade,
                 dominio_conteudo, relacionamento, pontos_positivos, aspectos_melhorar)
            )
            db.commit()
            db.close()
            return redirect(url_for('sucesso'))

        except (ValueError, KeyError):
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            db.close()
            return redirect(url_for('avaliar'))

    # GET - Mostrar formulário
    professores = db.execute('SELECT id, nome FROM professores ORDER BY nome').fetchall()

    # Construir dicionário de disciplinas por professor para o JavaScript
    disciplinas_por_prof = {}
    for prof in professores:
        discs = db.execute(
            '''SELECT d.id, d.nome
               FROM disciplinas d
               JOIN professor_disciplina pd ON d.id = pd.disciplina_id
               WHERE pd.professor_id = ?
               ORDER BY d.nome''',
            (prof['id'],)
        ).fetchall()
        disciplinas_por_prof[str(prof['id'])] = [
            {'id': d['id'], 'nome': d['nome']} for d in discs
        ]

    db.close()
    return render_template(
        'avaliar.html',
        professores=professores,
        disciplinas_json=json.dumps(disciplinas_por_prof, ensure_ascii=False)
    )


@app.route('/sucesso')
def sucesso():
    """Página de confirmação após envio de avaliação."""
    return render_template('sucesso.html')


# ==================== ROTAS DO PROFESSOR ====================

@app.route('/professor/login', methods=['GET', 'POST'])
def login_professor():
    """Login do professor por código de acesso."""
    if request.method == 'POST':
        codigo = request.form.get('codigo_acesso', '').strip()
        db = get_db()
        professor = db.execute(
            'SELECT id, nome FROM professores WHERE codigo_acesso = ?',
            (codigo,)
        ).fetchone()
        db.close()

        if professor:
            session['professor_id'] = professor['id']
            session['professor_nome'] = professor['nome']
            return redirect(url_for('dashboard'))
        else:
            flash('Código de acesso inválido. Tente novamente.', 'error')

    return render_template('login_professor.html')


@app.route('/professor/dashboard')
def dashboard():
    """Painel do professor com feedbacks recebidos."""
    if 'professor_id' not in session:
        flash('Faça login para acessar o painel.', 'error')
        return redirect(url_for('login_professor'))

    professor_id = session['professor_id']
    db = get_db()

    # Informações do professor
    professor = db.execute(
        'SELECT id, nome FROM professores WHERE id = ?',
        (professor_id,)
    ).fetchone()

    # Médias
    medias_row = db.execute(
        '''SELECT
            AVG(didatica) as didatica,
            AVG(pontualidade) as pontualidade,
            AVG(dominio_conteudo) as dominio,
            AVG(relacionamento) as relacionamento,
            COUNT(*) as total
           FROM avaliacoes
           WHERE professor_id = ?''',
        (professor_id,)
    ).fetchone()

    total_avaliacoes = medias_row['total'] if medias_row['total'] else 0

    class Medias:
        pass

    medias = Medias()
    if total_avaliacoes > 0:
        medias.didatica = medias_row['didatica']
        medias.pontualidade = medias_row['pontualidade']
        medias.dominio = medias_row['dominio']
        medias.relacionamento = medias_row['relacionamento']
        medias.geral = (
            medias.didatica + medias.pontualidade +
            medias.dominio + medias.relacionamento
        ) / 4
    else:
        medias.didatica = None
        medias.pontualidade = None
        medias.dominio = None
        medias.relacionamento = None
        medias.geral = None

    # Avaliações individuais (comentários)
    avaliacoes_rows = db.execute(
        '''SELECT a.pontos_positivos, a.aspectos_melhorar, a.data_criacao as data,
                  d.nome as disciplina
           FROM avaliacoes a
           JOIN disciplinas d ON a.disciplina_id = d.id
           WHERE a.professor_id = ?
           ORDER BY a.data_criacao DESC''',
        (professor_id,)
    ).fetchall()

    avaliacoes = []
    for row in avaliacoes_rows:
        avaliacoes.append({
            'pontos_positivos': row['pontos_positivos'],
            'aspectos_melhorar': row['aspectos_melhorar'],
            'data': row['data'],
            'disciplina': row['disciplina']
        })

    db.close()

    return render_template(
        'dashboard.html',
        professor=professor,
        medias=medias,
        total_avaliacoes=total_avaliacoes,
        avaliacoes=avaliacoes
    )


@app.route('/professor/logout')
def logout_professor():
    """Encerra a sessão do professor."""
    session.pop('professor_id', None)
    session.pop('professor_nome', None)
    flash('Sessão encerrada com sucesso.', 'info')
    return redirect(url_for('index'))


# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    # Criar banco se não existir
    if not os.path.exists(DB_PATH):
        print('Banco de dados não encontrado. Execute primeiro: python init_db.py')
    else:
        print('Servidor iniciando...')
        print('Acesse: http://127.0.0.1:5000')
    app.run(debug=True)
