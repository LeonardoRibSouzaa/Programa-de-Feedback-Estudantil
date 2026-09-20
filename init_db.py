import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'feedback.db')


def criar_banco():
    """Cria as tabelas do banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS professores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo_acesso TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS professor_disciplina (
            professor_id INTEGER NOT NULL,
            disciplina_id INTEGER NOT NULL,
            PRIMARY KEY (professor_id, disciplina_id),
            FOREIGN KEY (professor_id) REFERENCES professores(id),
            FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id)
        );

        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            professor_id INTEGER NOT NULL,
            disciplina_id INTEGER NOT NULL,
            didatica INTEGER NOT NULL CHECK(didatica BETWEEN 1 AND 5),
            pontualidade INTEGER NOT NULL CHECK(pontualidade BETWEEN 1 AND 5),
            dominio_conteudo INTEGER NOT NULL CHECK(dominio_conteudo BETWEEN 1 AND 5),
            relacionamento INTEGER NOT NULL CHECK(relacionamento BETWEEN 1 AND 5),
            pontos_positivos TEXT,
            aspectos_melhorar TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (professor_id) REFERENCES professores(id),
            FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id)
        );
    ''')

    conn.commit()
    conn.close()
    print('Tabelas criadas com sucesso.')


def popular_dados():
    """Insere dados de exemplo no banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verificar se já existem dados
    cursor.execute('SELECT COUNT(*) FROM professores')
    if cursor.fetchone()[0] > 0:
        print('Banco já possui dados. Pulando inserção.')
        conn.close()
        return

    # Professores de exemplo
    professores = [
        ('Prof. Ana Maria Silva', 'ana123'),
        ('Prof. Carlos Eduardo Santos', 'carlos123'),
        ('Prof. Fernanda Oliveira', 'fernanda123'),
        ('Prof. João Pedro Lima', 'joao123'),
        ('Prof. Maria Clara Souza', 'maria123'),
    ]
    cursor.executemany(
        'INSERT INTO professores (nome, codigo_acesso) VALUES (?, ?)',
        professores
    )

    # Disciplinas de exemplo
    disciplinas = [
        ('Matemática',),
        ('Português',),
        ('História',),
        ('Geografia',),
        ('Ciências',),
        ('Inglês',),
        ('Educação Física',),
        ('Programação',),
    ]
    cursor.executemany(
        'INSERT INTO disciplinas (nome) VALUES (?)',
        disciplinas
    )

    # Associar professores a disciplinas
    associacoes = [
        (1, 1), (1, 8),   # Ana: Matemática, Programação
        (2, 2), (2, 6),   # Carlos: Português, Inglês
        (3, 3), (3, 4),   # Fernanda: História, Geografia
        (4, 5), (4, 8),   # João: Ciências, Programação
        (5, 1), (5, 7),   # Maria: Matemática, Educação Física
    ]
    cursor.executemany(
        'INSERT INTO professor_disciplina (professor_id, disciplina_id) VALUES (?, ?)',
        associacoes
    )

    # Algumas avaliações de exemplo
    avaliacoes = [
        (1, 1, 5, 4, 5, 5, 'Excelente didática, explica muito bem.', 'Poderia usar mais exemplos práticos.'),
        (1, 1, 4, 5, 4, 4, 'Muito pontual e organizada.', 'As provas são muito difíceis.'),
        (2, 2, 3, 3, 4, 5, 'Muito atencioso com os alunos.', 'Poderia trazer mais atividades dinâmicas.'),
        (3, 3, 5, 5, 5, 4, 'Aulas muito interessantes.', 'Poderia usar mais recursos audiovisuais.'),
        (4, 5, 4, 4, 5, 3, 'Domina muito bem o conteúdo.', 'Poderia ser mais acessível para tirar dúvidas.'),
    ]
    cursor.executemany(
        '''INSERT INTO avaliacoes
           (professor_id, disciplina_id, didatica, pontualidade,
            dominio_conteudo, relacionamento, pontos_positivos, aspectos_melhorar)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        avaliacoes
    )

    conn.commit()
    conn.close()
    print('Dados de exemplo inseridos com sucesso.')


if __name__ == '__main__':
    criar_banco()
    popular_dados()
    print(f'Banco de dados criado em: {DB_PATH}')
