"""
Inicialização do banco de dados PostgreSQL
Programa de Feedback Estudantil
"""

import os

import psycopg2


def conectar_banco():
    """Conecta ao banco PostgreSQL usando DATABASE_URL."""
    return psycopg2.connect(
        os.environ['DATABASE_URL']
    )


def criar_banco():
    """Cria as tabelas do banco de dados."""

    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS professores (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            codigo_acesso TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS disciplinas (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS professor_disciplina (
            professor_id INTEGER NOT NULL,
            disciplina_id INTEGER NOT NULL,

            PRIMARY KEY (
                professor_id,
                disciplina_id
            ),

            FOREIGN KEY (professor_id)
                REFERENCES professores(id)
                ON DELETE CASCADE,

            FOREIGN KEY (disciplina_id)
                REFERENCES disciplinas(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS avaliacoes (
            id SERIAL PRIMARY KEY,

            professor_id INTEGER NOT NULL,
            disciplina_id INTEGER NOT NULL,

            didatica INTEGER NOT NULL
                CHECK (didatica BETWEEN 1 AND 5),

            pontualidade INTEGER NOT NULL
                CHECK (pontualidade BETWEEN 1 AND 5),

            dominio_conteudo INTEGER NOT NULL
                CHECK (dominio_conteudo BETWEEN 1 AND 5),

            relacionamento INTEGER NOT NULL
                CHECK (relacionamento BETWEEN 1 AND 5),

            pontos_positivos TEXT,
            aspectos_melhorar TEXT,

            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (professor_id)
                REFERENCES professores(id)
                ON DELETE CASCADE,

            FOREIGN KEY (disciplina_id)
                REFERENCES disciplinas(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        );
        '''
    )

    conn.commit()

    cursor.close()
    conn.close()

    print('Tabelas criadas com sucesso.')


def popular_dados():
    """Insere dados de exemplo no banco de dados."""

    conn = conectar_banco()
    cursor = conn.cursor()

    # Verificar se já existem professores
    cursor.execute(
        'SELECT COUNT(*) FROM professores'
    )

    quantidade = cursor.fetchone()[0]

    if quantidade > 0:
        print(
            'Banco já possui dados. '
            'Pulando inserção dos dados de exemplo.'
        )

        cursor.close()
        conn.close()

        return

    # ==================== CONFIGURAÇÕES ====================

    cursor.execute(
        '''
        INSERT INTO configuracoes
            (chave, valor)
        VALUES (%s, %s)
        ON CONFLICT (chave) DO NOTHING
        ''',
        (
            'senha_admin',
            'admin2026'
        )
    )

    print(
        'Senha padrão do administrador: admin2026'
    )

    # ==================== PROFESSORES ====================

    professores = [
        (
            'Prof. Ana Maria Silva',
            'ana123'
        ),
        (
            'Prof. Carlos Eduardo Santos',
            'carlos123'
        ),
        (
            'Prof. Fernanda Oliveira',
            'fernanda123'
        ),
        (
            'Prof. João Pedro Lima',
            'joao123'
        ),
        (
            'Prof. Maria Clara Souza',
            'maria123'
        )
    ]

    professor_ids = []

    for nome, codigo in professores:

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

        professor_id = cursor.fetchone()[0]

        professor_ids.append(professor_id)

    # ==================== DISCIPLINAS ====================

    disciplinas = [
        'Matemática',
        'Português',
        'História',
        'Geografia',
        'Ciências',
        'Inglês',
        'Educação Física',
        'Programação'
    ]

    disciplina_ids = []

    for nome in disciplinas:

        cursor.execute(
            '''
            INSERT INTO disciplinas
                (nome)
            VALUES (%s)
            RETURNING id
            ''',
            (nome,)
        )

        disciplina_id = cursor.fetchone()[0]

        disciplina_ids.append(disciplina_id)

    # ==================== ASSOCIAÇÕES ====================

    associacoes = [
        (
            professor_ids[0],
            disciplina_ids[0]
        ),
        (
            professor_ids[0],
            disciplina_ids[7]
        ),

        (
            professor_ids[1],
            disciplina_ids[1]
        ),
        (
            professor_ids[1],
            disciplina_ids[5]
        ),

        (
            professor_ids[2],
            disciplina_ids[2]
        ),
        (
            professor_ids[2],
            disciplina_ids[3]
        ),

        (
            professor_ids[3],
            disciplina_ids[4]
        ),
        (
            professor_ids[3],
            disciplina_ids[7]
        ),

        (
            professor_ids[4],
            disciplina_ids[0]
        ),
        (
            professor_ids[4],
            disciplina_ids[6]
        )
    ]

    cursor.executemany(
        '''
        INSERT INTO professor_disciplina
            (
                professor_id,
                disciplina_id
            )
        VALUES (%s, %s)
        ''',
        associacoes
    )

    # ==================== AVALIAÇÕES ====================

    avaliacoes = [
        (
            professor_ids[0],
            disciplina_ids[0],
            5,
            4,
            5,
            5,
            'Excelente didática, explica muito bem.',
            'Poderia usar mais exemplos práticos.'
        ),
        (
            professor_ids[0],
            disciplina_ids[0],
            4,
            5,
            4,
            4,
            'Muito pontual e organizada.',
            'As provas são muito difíceis.'
        ),
        (
            professor_ids[1],
            disciplina_ids[1],
            3,
            3,
            4,
            5,
            'Muito atencioso com os alunos.',
            'Poderia trazer mais atividades dinâmicas.'
        ),
        (
            professor_ids[2],
            disciplina_ids[2],
            5,
            5,
            5,
            4,
            'Aulas muito interessantes.',
            'Poderia usar mais recursos audiovisuais.'
        ),
        (
            professor_ids[3],
            disciplina_ids[4],
            4,
            4,
            5,
            3,
            'Domina muito bem o conteúdo.',
            'Poderia ser mais acessível para tirar dúvidas.'
        )
    ]

    cursor.executemany(
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
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ''',
        avaliacoes
    )

    conn.commit()

    cursor.close()
    conn.close()

    print(
        'Dados de exemplo inseridos com sucesso.'
    )


if __name__ == '__main__':

    criar_banco()

    popular_dados()

    print(
        'Banco PostgreSQL configurado com sucesso.'
    )