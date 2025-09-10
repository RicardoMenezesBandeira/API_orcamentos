from flask import Blueprint, request, jsonify, render_template, send_file
import os, json, re
from pathlib import Path  # ADICIONADO
from ..decorators.auth import token_required  # mantém o mesmo décorator
from ..services import orcamento_service as svc
from ..utils.helpers import get_data
from ..routes.misc_routes import get_dashboard

# BD_PREENCH = os.path.join("../bd", "json_preenchimento")
BD_PREENCH = Path("/app/bd/json_preenchimento")  # ALTERADO
from ..utils.helpers import get_data
bp = Blueprint("orcamento", __name__)

BD_PREENCH = Path("bd/json_preenchimento")
BD_EDICOES = Path("bd/edicoes")
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


@bp.route("/orcamento", methods=["GET"])    
@token_required
def listar_orcamentos(user_data):
    print("aqui")
    """
    Devolve todos os JSONs em bd/json_preenchimento
    visíveis ao usuário atual (vendedor ou admin).
    """
    arquivos = (BD_PREENCH.glob("*.json"))
    todos    = []

    # ➋  Nome e privilégio do usuário logado
    vendedor = get_data(user_data.get("user"))
    is_admin = vendedor.get("admin", False)

    for arq in arquivos:
        with arq.open(encoding="utf-8") as f:
            dados = json.load(f)

        if dados.get("vendedor") == vendedor.get("nome") or is_admin:
            todos.append(dados)

    return jsonify(todos), 200


@bp.route("/verification", methods=["GET"])
@token_required
def verificar_template(user_data):
    json_file = request.args.get('json_file')  # Padrão para 21.json
    base_path = "bd/json_preenchimento"  # Renomeado para clareza

    # 1. Lista os JSONs de controle para saber qual orçamento analisar
    try:
        arquivos = sorted(
            [f for f in os.listdir(base_path) if f.endswith('.json')],
            key=lambda f: os.path.getmtime(os.path.join(base_path, f))
        )
        if not arquivos:
            return "Nenhum JSON encontrado no diretório de controle.", 404
    except FileNotFoundError:
        return f"Diretório de controle '{base_path}' não encontrado.", 404

    # 2. Seleciona o arquivo de controle (ex: 21.json)
    json_file = request.args.get('json_file', arquivos[-1])
    if json_file not in arquivos:
        json_file = arquivos[-1]
    
    base_id = int(json_file.split('.')[0])

    # 3. Carrega o JSON de controle APENAS para pegar a lista de templates
    path_controle = os.path.join(base_path, json_file)
    with open(path_controle, encoding='utf-8') as f:
        dados_controle = json.load(f)

    templates = dados_controle.get('templates', [])
    if isinstance(templates, str):
        templates = [templates]
    
    # 4. Determina o índice do template atual (ex: 0 para Big, 1 para BossBR)
    idx = int(request.args.get('template_idx', 0) or 0)
    if idx >= len(templates):
        return get_dashboard()

    emp = templates[idx]  # Nome do template atual, ex: "Big"

    # 5. [NOVA LÓGICA] Carrega os dados do JSON específico do template
    # O caminho agora aponta para bd/edicoes/NOME_EMPRESA/XX.json
    
    base_path = os.path.join("bd", "json_preenchimento", json_file)
    edit_path = os.path.join("bd", "edicoes", emp, json_file)
    
    try:
        if os.path.exists(edit_path):
            with open(edit_path, encoding='utf-8') as f:
                dados = json.load(f)
        else:
            with open(base_path, encoding='utf-8') as f:
                dados = json.load(f)
    except FileNotFoundError:
        return f"Erro: Arquivo JSON não encontrado para o template '{emp}' em '{edit_path}' e  '{base_path}'", 404
    except json.JSONDecodeError:
        return f"Erro ao decodificar o JSON em '{edit_path}' ou e  '{base_path}'. Verifique o formato do arquivo.", 500

    # 6. [LÓGICA MOVIDA] O parsing de produtos agora opera nos 'dados' específicos do template
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

    # 7. O restante da lógica permanece o mesmo
    iframe_src = f"/template-PDF/orcamento_{str(base_id).zfill(3)}_{emp.lower()}.html"

    return render_template(
        'revisao.html',
        iframe_src=iframe_src,
        template_nome=emp,
        proximo_idx=idx + 1,
        dados=dados,  # Passa os dados específicos do template para o frontend
        json_file=json_file,
        id=base_id
    ), 200


@bp.route("/orcamento", methods=["GET"])      # já existia
@token_required
def mostrar_orcamentos_usuario(user_data):
    return svc.listar_orcamentos(user_data)


@bp.route('/delete/<id>', methods=['DELETE'])# ajeitar para deletar os #
@token_required
def deletar_orcamento(user_data, id):
    return svc.delete_orcamento(user_data,id)