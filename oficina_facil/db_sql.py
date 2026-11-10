import sqlite3
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as arquivo:
        db.executescript(arquivo.read().decode("utf8"))
    db.commit()


def listar_clientes():
    return get_db().execute("SELECT * FROM clientes ORDER BY nome").fetchall()


def buscar_cliente(id_cliente):
    return get_db().execute(
        "SELECT * FROM clientes WHERE id_cliente = ?", (id_cliente,)
    ).fetchone()


def criar_cliente(dados):
    db = get_db()
    db.execute("INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)", dados)
    db.commit()


def atualizar_cliente(dados):
    db = get_db()
    db.execute(
        "UPDATE clientes SET nome = ?, telefone = ?, email = ? WHERE id_cliente = ?", dados
    )
    db.commit()


def excluir_cliente(id_cliente):
    db = get_db()
    db.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
    db.commit()


def listar_veiculos():
    return get_db().execute("""
        SELECT v.*, c.nome AS cliente_nome
        FROM veiculos v INNER JOIN clientes c ON c.id_cliente = v.id_cliente
        ORDER BY v.modelo
    """).fetchall()


def criar_veiculo(dados):
    db = get_db()
    db.execute("""
        INSERT INTO veiculos (id_cliente, marca, modelo, placa, ano)
        VALUES (?, ?, ?, ?, ?)
    """, dados)
    db.commit()


def excluir_veiculo(id_veiculo):
    db = get_db()
    db.execute("DELETE FROM veiculos WHERE id_veiculo = ?", (id_veiculo,))
    db.commit()


def listar_servicos():
    return get_db().execute("SELECT * FROM servicos ORDER BY nome").fetchall()


def criar_servico(dados):
    db = get_db()
    db.execute(
        "INSERT INTO servicos (nome, descricao, preco) VALUES (?, ?, ?)", dados
    )
    db.commit()


def excluir_servico(id_servico):
    db = get_db()
    db.execute("DELETE FROM servicos WHERE id_servico = ?", (id_servico,))
    db.commit()


def listar_ordens():
    return get_db().execute("""
        SELECT os.*, v.marca, v.modelo, v.placa, c.nome AS cliente_nome
        FROM ordens_servico os
        INNER JOIN veiculos v ON v.id_veiculo = os.id_veiculo
        INNER JOIN clientes c ON c.id_cliente = v.id_cliente
        ORDER BY os.id_os DESC
    """).fetchall()


def criar_ordem(id_veiculo, ids_servicos):
    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO ordens_servico (id_veiculo, status, valor_total) VALUES (?, 'Aberta', 0)",
            (id_veiculo,),
        )
        id_os = cursor.lastrowid
        total = 0
        for id_servico in ids_servicos:
            servico = db.execute(
                "SELECT preco FROM servicos WHERE id_servico = ?", (id_servico,)
            ).fetchone()
            if servico is None:
                raise ValueError("Serviço inválido")
            preco = servico["preco"]
            total += preco
            db.execute("""
                INSERT INTO os_servicos (id_os, id_servico, quantidade, valor_unitario)
                VALUES (?, ?, 1, ?)
            """, (id_os, id_servico, preco))
        db.execute("UPDATE ordens_servico SET valor_total = ? WHERE id_os = ?", (total, id_os))
        db.commit()
    except Exception:
        db.rollback()
        raise


def atualizar_status_os(dados):
    db = get_db()
    db.execute("UPDATE ordens_servico SET status = ? WHERE id_os = ?", dados)
    db.commit()


def excluir_ordem(id_os):
    db = get_db()
    db.execute("DELETE FROM ordens_servico WHERE id_os = ?", (id_os,))
    db.commit()


def buscar_ordem(id_os):
    return get_db().execute("""
        SELECT os.*, v.marca, v.modelo, v.placa, c.nome AS cliente_nome
        FROM ordens_servico os
        INNER JOIN veiculos v ON v.id_veiculo = os.id_veiculo
        INNER JOIN clientes c ON c.id_cliente = v.id_cliente
        WHERE os.id_os = ?
    """, (id_os,)).fetchone()


def listar_itens_ordem(id_os):
    return get_db().execute("""
        SELECT s.nome, s.descricao, os_s.quantidade, os_s.valor_unitario,
               (os_s.quantidade * os_s.valor_unitario) AS subtotal
        FROM os_servicos os_s
        INNER JOIN servicos s ON s.id_servico = os_s.id_servico
        WHERE os_s.id_os = ?
    """, (id_os,)).fetchall()


def obter_indicadores():
    db = get_db()
    return {
        "clientes": db.execute("SELECT COUNT(*) FROM clientes").fetchone()[0],
        "veiculos": db.execute("SELECT COUNT(*) FROM veiculos").fetchone()[0],
        "ordens_abertas": db.execute(
            "SELECT COUNT(*) FROM ordens_servico WHERE status IN ('Aberta', 'Em andamento')"
        ).fetchone()[0],
        "faturamento": db.execute(
            "SELECT COALESCE(SUM(valor_total), 0) FROM ordens_servico WHERE status = 'Concluída'"
        ).fetchone()[0],
    }
