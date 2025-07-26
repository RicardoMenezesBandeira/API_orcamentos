from flask import Blueprint, request, jsonify, render_template, send_file
import os, json, re

from ..decorators.auth import token_required  # mantém o mesmo décorator
from ..services import orcamento_service as svc

bp = Blueprint("orcamento", __name__)


# ---------------------------------------------------------------------------
# Rotas equivalentes às que existiam em api.py
# ---------------------------------------------------------------------------

@bp.route("/preencher")
@token_required
def preencher(user_data):
    """Exibe a página geradorOrcamento.html (GET)."""
    return render_template("geradorOrcamento.html")


@bp.route("/postTemplate", methods=["POST", "GET"])
@token_required
def post_template(user_data):
    """Recebe dados do formulário (ou exibe a página, se GET)."""
    # O próprio service trata GET para manter compat
    return svc.receber_orcamento(user_data)


@bp.route("/verification/preview", methods=["POST"])
@token_required
def preview(user_data):
    """Gera preview HTML on‑the‑fly."""
    return svc.preview_template(user_data)


@bp.route("/verification/update", methods=["POST"])
@token_required
def update(user_data):
    """Salva correções do usuário em bd/edicoes."""
    return svc.atualiza_orcamento(user_data)


@bp.route("/download/<int:orcamento_id>/<template>")
@token_required
def download(user_data, orcamento_id: int, template: str):
    """Gera o PDF final para download."""
    return svc.download_orcamento(user_data, orcamento_id, template)



@bp.route("/orcamento", methods=['GET'])
@token_required
def exibir_orcamento(user_data):
    """Exibe os orçamentos feitos pelo usuário"""
    return svc.orcamento(user_data)




@bp.route("/verification", methods=["GET"])
@token_required
def verificar_template(user_data):
    """Mostra revisão do orçamento, permitindo correções campo a campo.
    Lógica copiada do api.py original para manter compatibilidade.
    """
    json_dir = "bd/json_preenchimento"

    # Lista arquivos JSON por data de modificação
    arquivos = sorted(
        [f for f in os.listdir(json_dir) if f.endswith('.json')],
        key=lambda f: os.path.getmtime(os.path.join(json_dir, f))
    )
    if not arquivos:
        return "Nenhum JSON encontrado", 404

    # Seleciona json_file solicitado ou o último
    json_file = request.args.get('json_file', arquivos[-1])
    if json_file not in arquivos:
        json_file = arquivos[-1]

    # Carrega dados
    path = os.path.join(json_dir, json_file)
    with open(path, encoding='utf-8') as f:
        dados = json.load(f)

    # Reaplica parsing de produtos se for string
    raw = dados.get('produtos', '')
    if isinstance(raw, str):
        lst = []
        for trecho in raw.split('</tr>'):
            if '<tr>' not in trecho:
                continue
            cells = re.findall(r'<td>(.*?)</td>', trecho, flags=re.DOTALL)
            lst.append({
                'numero': cells[0] if len(cells) > 0 else '',
                'produto': cells[1] if len(cells) > 1 else '',
                'quantidade': cells[2] if len(cells) > 2 else '',
                'unidade': cells[3] if len(cells) > 3 else '',
                'valor_unitario': cells[4] if len(cells) > 4 else '',
                'total_local': cells[5] if len(cells) > 5 else ''
            })
        dados['produtos'] = lst

    # Determina template atual / próximo índice
    templates = dados.get('templates', [])
    if isinstance(templates, str):
        templates = [templates]
    idx = int(request.args.get('template_idx', 0) or 0)
    if idx >= len(templates):
        return ("<h2>Todos os templates foram revisados!</h2>"
                "<a href='/dashboard'>Voltar para Início</a>"), 200

    emp = templates[idx]
    base_id = int(json_file.split('.')[0])
    iframe_src = f"/template-PDF/orcamento_{str(base_id).zfill(3)}_{emp.lower()}.html"

    return render_template(
        'revisao.html',
        iframe_src=iframe_src,
        template_nome=emp,
        proximo_idx=idx+1,
        dados=dados,
        json_file=json_file,
        id=base_id
    ), 200
