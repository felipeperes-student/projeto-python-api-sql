import os
import click
from flask import Flask, flash, redirect, render_template, request, url_for
import db_sql

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-dev-oficina-facil")
app.config["DATABASE"] = os.environ.get("DATABASE", "oficina.db")

app.teardown_appcontext(db_sql.close_db)


@app.cli.command("init-db")
def init_db_command():
    """Cria as tabelas do banco de dados."""
    db_sql.init_db()
    click.echo("Banco de dados inicializado com sucesso.")


@app.route("/")
def index():
    dados = db_sql.obter_indicadores()
    ultimas_os = db_sql.listar_ordens()
    return render_template("index.html", dados=dados, ordens=ultimas_os[:5])


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/contato")
def contato():
    return render_template("contato.html")


# CLIENTES
@app.route("/clientes")
def clientes():
    return render_template("clientes.html", clientes=db_sql.listar_clientes())


@app.route("/clientes/novo", methods=["GET", "POST"])
def novo_cliente():
    if request.method == "POST":
        dados = (
            request.form["nome"].strip(),
            request.form.get("telefone", "").strip(),
            request.form.get("email", "").strip(),
        )
        if not dados[0]:
            flash("Informe o nome do cliente.", "erro")
        else:
            db_sql.criar_cliente(dados)
            flash("Cliente cadastrado com sucesso.", "sucesso")
            return redirect(url_for("clientes"))
    return render_template("form_cliente.html", cliente=None)


@app.route("/clientes/<int:id_cliente>/editar", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    cliente = db_sql.buscar_cliente(id_cliente)
    if cliente is None:
        return render_template("404.html"), 404
    if request.method == "POST":
        db_sql.atualizar_cliente((
            request.form["nome"].strip(),
            request.form.get("telefone", "").strip(),
            request.form.get("email", "").strip(),
            id_cliente,
        ))
        flash("Cliente atualizado.", "sucesso")
        return redirect(url_for("clientes"))
    return render_template("form_cliente.html", cliente=cliente)


@app.post("/clientes/<int:id_cliente>/excluir")
def excluir_cliente(id_cliente):
    try:
        db_sql.excluir_cliente(id_cliente)
        flash("Cliente excluído.", "sucesso")
    except Exception:
        flash("Não foi possível excluir: verifique se o cliente possui veículos cadastrados.", "erro")
    return redirect(url_for("clientes"))


# VEÍCULOS
@app.route("/veiculos")
def veiculos():
    return render_template("veiculos.html", veiculos=db_sql.listar_veiculos(), clientes=db_sql.listar_clientes())


@app.route("/veiculos/novo", methods=["GET", "POST"])
def novo_veiculo():
    clientes = db_sql.listar_clientes()
    if request.method == "POST":
        db_sql.criar_veiculo((
            request.form["id_cliente"], request.form["marca"].strip(),
            request.form["modelo"].strip(), request.form["placa"].strip().upper(),
            request.form.get("ano") or None,
        ))
        flash("Veículo cadastrado.", "sucesso")
        return redirect(url_for("veiculos"))
    return render_template("form_veiculo.html", clientes=clientes)


@app.post("/veiculos/<int:id_veiculo>/excluir")
def excluir_veiculo(id_veiculo):
    try:
        db_sql.excluir_veiculo(id_veiculo)
        flash("Veículo excluído.", "sucesso")
    except Exception:
        flash("Não foi possível excluir um veículo que possui ordens de serviço.", "erro")
    return redirect(url_for("veiculos"))


# SERVIÇOS
@app.route("/servicos")
def servicos():
    return render_template("servicos.html", servicos=db_sql.listar_servicos())


@app.route("/servicos/novo", methods=["GET", "POST"])
def novo_servico():
    if request.method == "POST":
        db_sql.criar_servico((
            request.form["nome"].strip(),
            request.form.get("descricao", "").strip(),
            request.form["preco"],
        ))
        flash("Serviço cadastrado.", "sucesso")
        return redirect(url_for("servicos"))
    return render_template("form_servico.html")


@app.post("/servicos/<int:id_servico>/excluir")
def excluir_servico(id_servico):
    try:
        db_sql.excluir_servico(id_servico)
        flash("Serviço excluído.", "sucesso")
    except Exception:
        flash("Não foi possível excluir um serviço utilizado em uma ordem.", "erro")
    return redirect(url_for("servicos"))


# ORDENS DE SERVIÇO
@app.route("/ordens")
def ordens():
    return render_template("ordens.html", ordens=db_sql.listar_ordens())


@app.route("/ordens/nova", methods=["GET", "POST"])
def nova_ordem():
    veiculos = db_sql.listar_veiculos()
    servicos = db_sql.listar_servicos()
    if request.method == "POST":
        id_veiculo = request.form["id_veiculo"]
        ids_servicos = request.form.getlist("servicos")
        if not ids_servicos:
            flash("Selecione ao menos um serviço.", "erro")
        else:
            db_sql.criar_ordem(id_veiculo, ids_servicos)
            flash("Ordem de serviço criada.", "sucesso")
            return redirect(url_for("ordens"))
    return render_template("form_ordem.html", veiculos=veiculos, servicos=servicos)


@app.post("/ordens/<int:id_os>/status")
def atualizar_status_os(id_os):
    status = request.form["status"]
    if status in ("Aberta", "Em andamento", "Concluída", "Cancelada"):
        db_sql.atualizar_status_os((status, id_os))
        flash("Status atualizado.", "sucesso")
    return redirect(url_for("ordens"))


@app.post("/ordens/<int:id_os>/excluir")
def excluir_ordem(id_os):
    db_sql.excluir_ordem(id_os)
    flash("Ordem excluída.", "sucesso")
    return redirect(url_for("ordens"))


@app.route("/ordem/<int:id_os>")
def detalhe_ordem(id_os):
    ordem = db_sql.buscar_ordem(id_os)
    if ordem is None:
        return render_template("404.html"), 404
    itens = db_sql.listar_itens_ordem(id_os)
    return render_template("detalhe_ordem.html", ordem=ordem, itens=itens)


@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
