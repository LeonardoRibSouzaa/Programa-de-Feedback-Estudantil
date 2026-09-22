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

import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, redirect, url_for, flash, session


app = Flask(__name__)

app.secret_key = os.environ.get(
    'SECRET_KEY',
    'feedback-estudantil-extensionista-2026'
)


class DatabaseConnection:
    """
    Wrapper para manter a mesma facilidade de uso do SQLite,
    mas utilizando PostgreSQL.
    """

    def __init__(self):
        self.conn = psycopg2.connect(os.environ['DATABASE_URL'])

    def execute(self, query, params=None):
        cursor = self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        cursor.execute(query, params)
        return cursor

    def cursor(self):
        return self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def get_db():
    """Retorna uma conexão com o banco PostgreSQL."""
    return DatabaseConnection()


def get_admin_senha():
    """Busca a senha do administrador no banco de dados."""
    db = get_db()

    try:
        cursor = db.execute(
            "SELECT valor FROM configuracoes WHERE chave = 'senha_admin'"
        )
        row = cursor.fetchone()

        return row['valor'] if row else 'admin2026'

    finally:
        db.close()


# ==================== ROTAS PRINCIPAIS ====================

@app.route('/')
def index():
    """Página inicial."""
    return render_template('index.html')


@app.route('/aluno/avaliar', methods=['GET', 'POST'])
def avaliar():
    """Formulário de avaliação (GET) e processamento (POST)."""
    db = get_db()

    try:
        if request.method == 'POST':
            try:
                professor_id = int(request.form['professor_id'])
                disciplina_id = int(request.form['disciplina_id'])
                didatica = int(request.form['didatica'])
                pontualidade = int(request.form['pontualidade'])
                dominio_conteudo = int(request.form['dominio_conteudo'])
                relacionamento = int(request.form['relacionamento'])

                pontos_positivos = request.form.get(
                    'pontos_positivos', ''
                ).strip()

                aspectos_melhorar = request.form.get(
                    'aspectos_melhorar', ''
                ).strip()

                # Validar notas entre 1 e 5
                for nota in [
                    didatica,
                    pontualidade,
                    dominio_conteudo,
                    relacionamento
                ]:
                    if nota < 1 or nota > 5:
                        flash(
                            'As notas devem estar entre 1 e 5.',
                            'error'
                        )
                        return redirect(url_for('avaliar'))

                db.execute(
                    '''
                    INSERT INTO avaliacoes
                    (
                        professor_id,
                        disciplina_id,
                        didatica,
                        pontualidade,
                        dominio_conteudo,
                        relacionamento,
                        pontos_positivos,
                        aspectos_melhorar
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ''',
                    (
                        professor_id,
                        disciplina_id,
                        didatica,
                        pontualidade,
                        dominio_conteudo,
                        relacionamento,
                        pontos_positivos,
                        aspectos_melhorar
                    )
                )

                db.commit()

                return redirect(url_for('sucesso'))

            except (ValueError, KeyError):
                db.rollback()

                flash(
                    'Por favor, preencha todos os campos obrigatórios.',
                    'error'
                )

                return redirect(url_for('avaliar'))

        # GET - Mostrar formulário
        cursor = db.execute(
            '''
            SELECT id, nome
            FROM professores
            ORDER BY nome
            '''
        )

        professores = cursor.fetchall()

        # Construir dicionário de disciplinas por professor para o JavaScript
        disciplinas_por_prof = {}

        for prof in professores:
            cursor = db.execute(
                '''
                SELECT d.id, d.nome
                FROM disciplinas d
                JOIN professor_disciplina pd
                    ON d.id = pd.disciplina_id
                WHERE pd.professor_id = %s
                ORDER BY d.nome
                ''',
                (prof['id'],)
            )

            discs = cursor.fetchall()

            disciplinas_por_prof[str(prof['id'])] = [
                {
                    'id': d['id'],
                    'nome': d['nome']
                }
                for d in discs
            ]

        return render_template(
            'avaliar.html',
            professores=professores,
            disciplinas_json=json.dumps(
                disciplinas_por_prof,
                ensure_ascii=False
            )
        )

    finally:
        db.close()


@app.route('/sucesso')
def sucesso():
    """Página de confirmação após envio de avaliação."""
    return render_template('sucesso.html')


# ==================== ROTAS DO PROFESSOR ====================

@app.route('/professor/login', methods=['GET', 'POST'])
def login_professor():
    """Login do professor por código de acesso."""

    if request.method == 'POST':
        codigo = request.form.get(
            'codigo_acesso',
            ''
        ).strip()

        db = get_db()

        try:
            cursor = db.execute(
                '''
                SELECT id, nome
                FROM professores
                WHERE codigo_acesso = %s
                ''',
                (codigo,)
            )

            professor = cursor.fetchone()

        finally:
            db.close()

        if professor:
            session['professor_id'] = professor['id']
            session['professor_nome'] = professor['nome']

            return redirect(url_for('dashboard'))

        flash(
            'Código de acesso inválido. Tente novamente.',
            'error'
        )

    return render_template('login_professor.html')


@app.route('/professor/dashboard')
def dashboard():
    """Painel do professor com feedbacks recebidos."""

    if 'professor_id' not in session:
        flash(
            'Faça login para acessar o painel.',
            'error'
        )

        return redirect(url_for('login_professor'))

    professor_id = session['professor_id']

    db = get_db()

    try:
        # Informações do professor
        cursor = db.execute(
            '''
            SELECT id, nome
            FROM professores
            WHERE id = %s
            ''',
            (professor_id,)
        )

        professor = cursor.fetchone()

        # Médias
        cursor = db.execute(
            '''
            SELECT
                AVG(didatica) AS didatica,
                AVG(pontualidade) AS pontualidade,
                AVG(dominio_conteudo) AS dominio,
                AVG(relacionamento) AS relacionamento,
                COUNT(*) AS total
            FROM avaliacoes
            WHERE professor_id = %s
            ''',
            (professor_id,)
        )

        medias_row = cursor.fetchone()

        total_avaliacoes = (
            medias_row['total']
            if medias_row['total']
            else 0
        )

        class Medias:
            pass

        medias = Medias()

        if total_avaliacoes > 0:
            medias.didatica = medias_row['didatica']
            medias.pontualidade = medias_row['pontualidade']
            medias.dominio = medias_row['dominio']
            medias.relacionamento = medias_row['relacionamento']

            medias.geral = (
                medias.didatica +
                medias.pontualidade +
                medias.dominio +
                medias.relacionamento
            ) / 4

        else:
            medias.didatica = None
            medias.pontualidade = None
            medias.dominio = None
            medias.relacionamento = None
            medias.geral = None

        # Avaliações individuais
        cursor = db.execute(
            '''
            SELECT
                a.pontos_positivos,
                a.aspectos_melhorar,
                a.data_criacao AS data,
                d.nome AS disciplina
            FROM avaliacoes a
            JOIN disciplinas d
                ON a.disciplina_id = d.id
            WHERE a.professor_id = %s
            ORDER BY a.data_criacao DESC
            ''',
            (professor_id,)
        )

        avaliacoes_rows = cursor.fetchall()

        avaliacoes = []

        for row in avaliacoes_rows:
            avaliacoes.append({
                'pontos_positivos': row['pontos_positivos'],
                'aspectos_melhorar': row['aspectos_melhorar'],
                'data': row['data'],
                'disciplina': row['disciplina']
            })

        return render_template(
            'dashboard.html',
            professor=professor,
            medias=medias,
            total_avaliacoes=total_avaliacoes,
            avaliacoes=avaliacoes
        )

    finally:
        db.close()


@app.route('/professor/logout')
def logout_professor():
    """Encerra a sessão do professor."""

    session.pop('professor_id', None)
    session.pop('professor_nome', None)

    flash(
        'Sessão encerrada com sucesso.',
        'info'
    )

    return redirect(url_for('index'))


# ==================== ADMINISTRAÇÃO ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def login_admin():
    """Login do administrador."""

    if session.get('admin_logado'):
        return redirect(url_for('admin'))

    if request.method == 'POST':
        senha = request.form.get(
            'senha_admin',
            ''
        )

        if senha == get_admin_senha():
            session['admin_logado'] = True

            return redirect(url_for('admin'))

        flash(
            'Senha incorreta. Acesso negado.',
            'error'
        )

    return render_template('login_admin.html')


@app.route('/admin/logout')
def logout_admin():
    """Encerra a sessão do administrador."""

    session.pop('admin_logado', None)

    flash(
        'Sessão de administrador encerrada.',
        'info'
    )

    return redirect(url_for('index'))


@app.route('/admin/alterar-senha', methods=['POST'])
def alterar_senha_admin():
    """Permite ao administrador trocar sua senha."""

    if not session.get('admin_logado'):
        return redirect(url_for('login_admin'))

    senha_atual = request.form.get(
        'senha_atual',
        ''
    )

    senha_nova = request.form.get(
        'senha_nova',
        ''
    )

    senha_confirmar = request.form.get(
        'senha_confirmar',
        ''
    )

    if senha_atual != get_admin_senha():

        flash(
            'A senha atual está incorreta.',
            'error'
        )

    elif len(senha_nova) < 4:

        flash(
            'A nova senha deve ter pelo menos 4 caracteres.',
            'error'
        )

    elif senha_nova != senha_confirmar:

        flash(
            'A nova senha e a confirmação não coincidem.',
            'error'
        )

    else:
        db = get_db()

        try:
            db.execute(
                '''
                UPDATE configuracoes
                SET valor = %s
                WHERE chave = 'senha_admin'
                ''',
                (senha_nova,)
            )

            db.commit()

            flash(
                'Senha de administrador alterada com sucesso!',
                'success'
            )

        finally:
            db.close()

    return redirect(url_for('admin'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Painel de administração."""

    if not session.get('admin_logado'):
        flash(
            'Faça login como administrador para acessar esta área.',
            'error'
        )

        return redirect(url_for('login_admin'))

    db = get_db()

    try:
        if request.method == 'POST':

            nome = request.form.get(
                'nome',
                ''
            ).strip()

            codigo = request.form.get(
                'codigo_acesso',
                ''
            ).strip()

            disciplinas_selecionadas = request.form.getlist(
                'disciplinas'
            )

            if nome and codigo and disciplinas_selecionadas:

                try:
                    cursor = db.cursor()

                    # PostgreSQL utiliza RETURNING para obter o ID criado
                    cursor.execute(
                        '''
                        INSERT INTO professores
                            (nome, codigo_acesso)
                        VALUES (%s, %s)
                        RETURNING id
                        ''',
                        (
                            nome,
                            codigo
                        )
                    )

                    professor_id = cursor.fetchone()['id']

                    # Vincular o professor às disciplinas
                    for disc_id in disciplinas_selecionadas:

                        cursor.execute(
                            '''
                            INSERT INTO professor_disciplina
                                (professor_id, disciplina_id)
                            VALUES (%s, %s)
                            ''',
                            (
                                professor_id,
                                int(disc_id)
                            )
                        )

                    db.commit()

                    flash(
                        f'Professor(a) {nome} cadastrado(a) com sucesso!',
                        'success'
                    )

                except psycopg2.IntegrityError:
                    db.rollback()

                    flash(
                        'Erro: Já existe um professor com este código de acesso.',
                        'error'
                    )

            else:
                flash(
                    'Preencha o nome, código e selecione pelo menos uma disciplina.',
                    'error'
                )

            return redirect(url_for('admin'))

        # GET - Buscar disciplinas
        cursor = db.execute(
            '''
            SELECT id, nome
            FROM disciplinas
            ORDER BY nome
            '''
        )

        todas_disciplinas = cursor.fetchall()

        # GET - Buscar professores e disciplinas
        cursor = db.execute(
            '''
            SELECT
                p.id,
                p.nome,
                p.codigo_acesso,
                STRING_AGG(d.nome, ', ' ORDER BY d.nome) AS disciplinas
            FROM professores p
            LEFT JOIN professor_disciplina pd
                ON p.id = pd.professor_id
            LEFT JOIN disciplinas d
                ON pd.disciplina_id = d.id
            GROUP BY
                p.id,
                p.nome,
                p.codigo_acesso
            ORDER BY p.nome
            '''
        )

        professores_rows = cursor.fetchall()

        return render_template(
            'admin.html',
            professores=professores_rows,
            disciplinas=todas_disciplinas
        )

    finally:
        db.close()


@app.route('/admin/disciplina', methods=['POST'])
def adicionar_disciplina():
    """Cadastra uma nova disciplina."""

    if not session.get('admin_logado'):
        return redirect(url_for('login_admin'))

    nome = request.form.get(
        'nome',
        ''
    ).strip()

    if nome:

        db = get_db()

        try:
            db.execute(
                '''
                INSERT INTO disciplinas (nome)
                VALUES (%s)
                ''',
                (nome,)
            )

            db.commit()

            flash(
                f'Disciplina "{nome}" adicionada com sucesso!',
                'success'
            )

        finally:
            db.close()

    else:
        flash(
            'O nome da disciplina não pode ficar em branco.',
            'error'
        )

    return redirect(url_for('admin'))


@app.route('/admin/excluir/<int:id>', methods=['POST'])
def excluir_professor(id):
    """Exclui um professor e todas as suas dependências."""

    if not session.get('admin_logado'):
        return redirect(url_for('login_admin'))

    db = get_db()

    try:
        cursor = db.cursor()

        # 1. Apagar avaliações
        cursor.execute(
            '''
            DELETE FROM avaliacoes
            WHERE professor_id = %s
            ''',
            (id,)
        )

        # 2. Apagar vínculos com disciplinas
        cursor.execute(
            '''
            DELETE FROM professor_disciplina
            WHERE professor_id = %s
            ''',
            (id,)
        )

        # 3. Apagar professor
        cursor.execute(
            '''
            DELETE FROM professores
            WHERE id = %s
            ''',
            (id,)
        )

        db.commit()

        flash(
            'Professor excluído com sucesso!',
            'success'
        )

    finally:
        db.close()

    return redirect(url_for('admin'))


# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':

    print('Servidor iniciando...')
    print('Acesse: http://127.0.0.1:5000')

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )