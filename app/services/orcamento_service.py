from __future__ import annotations

import os
import json
import re
import traceback
from pathlib import Path

from flask import request, jsonify, url_for, make_response, current_app, render_template
from weasyprint import HTML

from ..utils.formatters import formatar_cnpj, formatar_cpf, formatar_dinheiro_brl
from ..utils.helpers import get_data

# Diretórios base (relativos ao repo)
BD_PREENCH = Path('bd/json_preenchimento')
BD_EDICOES = Path('bd/edicoes')
TPL_DIR    = Path('template-PDF')


# REMOVIDO: Funções de normalização não são mais necessárias
# Todos os templates agora usam lowercase consistentemente



def receber_orcamento(user_data):
    print(f"[INFO] receber_orcamento called by user: {user_data.get('nome')}")
    if request.method == 'GET':
        print("[DEBUG] GET request para gerarOrcamento.html")
        return render_template("geradorOrcamento.html")

    dados = request.get_json(force=True)
    print(f"[DEBUG] Payload recebido: {dados}")

    # Converte produtos em HTML
    itens = dados.get("produtos", [])
    
    html_rows = ''.join(
        f"<tr><td>{i['numero']}</td><td>{i['produto']}</td>"
        f"<td>{i['quantidade']}</td><td>{i['unidade']}</td>"
        f"<td>{i['valor_unitario']}</td><td>{i['total_local']}</td></tr>"
        for i in itens
    )
    dados["produtos"] = html_rows
    print(f"[DEBUG] Converted produtos to HTML rows.")

    # Inicializa dinamicamente o campo edicoes
    templates = dados.get('templates', [])
    if isinstance(templates, str):
        templates = [templates]
    dados['templates'] = templates
    dados['edicoes'] = [False] * len(templates)
    print(f"[DEBUG] Inicialized edicoes: {dados['edicoes']}")

    # Prepara diretório e identifica novo ID
    pasta = "bd/json_preenchimento"
    os.makedirs(pasta, exist_ok=True)
    files = [f for f in os.listdir(pasta) if f.endswith('.json')]
    ids = [int(f.split('.')[0]) for f in files if f.split('.')[0].isdigit()]
    nid = max(ids) + 1 if ids else 1
    dados["id"] = nid
    if (dados.get("numero") ==""):
        dados["numero"] = str(dados.get("id")).zfill(4)
    print(f"[DEBUG] Set numero: {dados['numero']}")
    print(f"[INFO] Assigned new orcamento ID: {nid}")

    # Preenche vendedor a partir do usuário logado
    nome_user = user_data.get("user")
    dados_func = get_data(nome_user)
    dados["vendedor"] = dados_func.get("nome")
    print(f"[DEBUG] Set vendedor: {dados['vendedor']}")

    # Salva JSON base em json_preenchimento
    path = os.path.join(pasta, f"{nid}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Saved base JSON to {path}")

    return jsonify({
        "mensagem": f"Orçamentos salvos para {', '.join(templates)}.",
        "id": nid
    }), 200



def preview_template(user_data):
    import traceback

    print(f"[INFO] preview_template called by user: {user_data.get('nome')}")
    correcoes = request.get_json(force=True)
    print(f"[DEBUG] Correções recebidas keys: {list(correcoes.keys())}")
    
    # CORREÇÃO: Normaliza template para garantir case correto
    tpl = correcoes.get('template').lower()
    
    json_file = correcoes.get('json_file')
    print(f"[DEBUG] Preview for template={tpl}, json_file={json_file}")

    # 1) Carrega JSON base
    base_path = os.path.join('bd/json_preenchimento', json_file)
    print(f"[DEBUG] Loading base JSON from {base_path}")
    with open(base_path, 'r', encoding='utf-8') as f:
        base_data = json.load(f)
    templates = base_data.get('templates', [])
    edicoes   = base_data.get('edicoes', [False] * len(templates))

    # Ajusta tamanho de edicoes se necessário
    if len(edicoes) != len(templates):
        edicoes = [False] * len(templates)
        print(f"[WARNING] Adjusted edicoes length: {edicoes}")

    # 2) Carrega JSON editado se houver
    orig = base_data
    if tpl in templates:
        idx = templates.index(tpl)
        if edicoes[idx]:
            edit_path = os.path.join('bd/edicoes', tpl, json_file)
            if os.path.exists(edit_path):
                print(f"[DEBUG] Loading edited JSON from {edit_path}")
                with open(edit_path, 'r', encoding='utf-8') as f:
                    orig = json.load(f)
            else:
                print(f"[WARNING] Edited JSON not found, falling back to base")
        else:
            print(f"[DEBUG] Using base JSON for preview")
    else:
        print(f"[ERROR] Template '{tpl}' not in templates list, using base")

    # 3) Remover lista de produtos vazios se for o caso
    prod_corr = correcoes.get('produtos')
    if isinstance(prod_corr, list) and prod_corr:
        todos_vazios = all(item.get('numero','') == '' for item in prod_corr)
        if todos_vazios:
            print("[DEBUG] Removendo correcoes['produtos'] porque todos itens estão vazios")
            correcoes.pop('produtos')

    # 4) Aplica as correções recebidas
    novo = orig.copy()
    novo['templates'] = [tpl]
    if novo.get('numero') == '':
        novo['numero'] = str(novo.get('id')).zfill(4)
    for k, v in correcoes.items():
        if k not in ('template', 'json_file'):
            novo[k] = v
            print(f"[DEBUG] Applied correction {k}={v!r}")

    # 5) Reconstrói produtos apenas se vieram como lista válida
    p = novo.get('produtos')

    if isinstance(p, list):
        try:
            print(f"[DEBUG] Reconstruindo lista de produtos, {len(p)} itens")
            rows = []
            valor_total = 0.0
            for item in p:
                quantidade_item = item.get('quantidade', '0').replace(',', '.')
                q = float(quantidade_item or 0)
                valor_unit = item.get('valor_unitario', '0').replace(',', '.')
                v = float(valor_unit or 0)
                total = q * v
                valor_total += total
                rows.append(
                    '<tr>'
                    f'<td>{item.get("numero")}</td>'
                    f'<td>{item.get("produto")}</td>'
                    f'<td>{q}</td>'
                    f'<td>{item.get("unidade")}</td>'
                    f'<td>{formatar_dinheiro_brl(v)}</td>'
                    f'<td>{formatar_dinheiro_brl(total)}</td>'
                    '</tr>'
                )
            novo['produtos']    = ''.join(rows)
            novo['valor_total'] = formatar_dinheiro_brl(valor_total)
            print(f"[DEBUG] Reconstrução de produtos OK")
        except Exception as e:
            print(f"[ERROR] Falha ao reconstruir produtos: {e}")
            traceback.print_exc()
    else:
        print("[DEBUG] Produto permanece como string HTML (não era lista)")

    # 6) Injeta no template e retorna HTML
    placeholder = os.path.join('template-PDF', f"{tpl}_placeholders.html")
    if len(novo.get('cnpj')) == 14:
        novo['cnpj'] = formatar_cnpj(novo['cnpj'])
    else:
        novo['cnpj'] = formatar_cpf(novo['cnpj'])
    
    if not os.path.exists(placeholder):
        print(f"[WARNING] Placeholder not found: {placeholder}")
        html = "<p>Template placeholder não encontrado.</p>"
    else:
        print(f"[DEBUG] Injecting data into {placeholder}")
        html = open(placeholder, encoding='utf-8').read()
        for k, v in novo.items():
            html = html.replace(f"{{{k}}}", str(v))
        html = html.replace('href="/css/', 'href="' + url_for('static', filename='css/'))
        html = html.replace('src="/img/', 'src="' + url_for('static', filename='img/'))
    print("[INFO] Returning preview HTML")
    return jsonify({'preview_html': html}), 200



def atualiza_orcamento(user_data):
    print(f"[INFO] atualiza_orcamento called by user: {user_data.get('nome')}")
    correcoes = request.get_json(force=True)
    
    # CORREÇÃO: Normaliza template para garantir case correto ao salvar
    tpl = correcoes.get('template').lower()
    
    json_file = correcoes.get('json_file')
    print(f"[DEBUG] Received corrections for template={tpl}, json_file={json_file}")

    # Carrega JSON base
    base_path = os.path.join('bd/json_preenchimento', json_file)
    with open(base_path, 'r', encoding='utf-8') as f:
        base_data = json.load(f)
    templates = base_data.get('templates', [])
    edicoes = base_data.get('edicoes', [False] * len(templates))

    # Ajusta tamanho de edicoes se necessário
    if len(edicoes) != len(templates):
        edicoes = [False] * len(templates)
        print(f"[WARNING] Adjusted edicoes length: {edicoes}")

    # Marca edição
    try:
        idx = templates.index(tpl)
        edicoes[idx] = True
        print(f"[DEBUG] Marked edicoes[{idx}] = True")
    except ValueError:
        print(f"[ERROR] Template '{tpl}' not found in templates list")

    base_data['edicoes'] = edicoes

    # Sobrescreve JSON base
    with open(base_path, 'w', encoding='utf-8') as f:
        json.dump(base_data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Updated base JSON edicoes at: {base_path}")

    # Prepara diretório de edições e salva JSON editado
    # IMPORTANTE: Usa o template normalizado para criar diretório com case correto
    edit_dir = os.path.join('bd/edicoes', tpl)
    os.makedirs(edit_dir, exist_ok=True)
    edit_path = os.path.join(edit_dir, json_file)
    edited_data = base_data.copy()
    for k, v in correcoes.items():
        if k not in ('template', 'json_file'):
            edited_data[k] = v
            print(f"[DEBUG] Updated field '{k}' in edited_data")

    with open(edit_path, 'w', encoding='utf-8') as f:
        json.dump(edited_data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Saved edited JSON to {edit_path}")

    # Gera HTML atualizado para o template editado
    tpl_dir = 'template-PDF'
    placeholder_file = os.path.join(tpl_dir, f"{tpl}_placeholders.html")
    if not os.path.exists(placeholder_file):
        print(f"[WARNING] Placeholder file not found: {placeholder_file}")

    return jsonify({"mensagem": f"Template '{tpl}' atualizado e salvo."}), 200



def download_orcamento(user_data, orcamento_id, template):
    print(f"[DEBUG] download_orcamento called: ID={orcamento_id}, template='{template}'")

    # Template já deve estar em lowercase - apenas garantindo
    template = template.lower()
    print(f"[DEBUG] Template em lowercase: '{template}'")

    # 1) Monta paths possíveis - usa template normalizado (case correto)
    path_edicoes = os.path.join('bd', 'edicoes', template, f'{orcamento_id}.json')
    path_base    = os.path.join('bd', 'json_preenchimento', f'{orcamento_id}.json')
    print(f"[DEBUG] Paths: edicoes='{path_edicoes}', base='{path_base}'")
    if os.path.exists(path_edicoes):
        json_path = path_edicoes
        print(f"[DEBUG] Usando JSON editado: {json_path}")
    elif os.path.exists(path_base):
        json_path = path_base
        print(f"[DEBUG] Usando JSON base: {json_path}")
    else:
        return jsonify({'erro': 'JSON não encontrado em edicoes nem em json_preenchimento'}), 404

    # 2) Carrega JSON
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    # 3) Converte lista de produtos em HTML + calcula valor_total
    produtos = data.get('produtos')
    if isinstance(produtos, list):
        rows = []
        valor_total = 0.0
        for item in produtos:
            quantidade_item = item.get('quantidade', '0').replace(',', '.')
            q = float(quantidade_item or 0)
            valor_unit = item.get('valor_unitario', '0').replace(',', '.')
            v = float(valor_unit or 0)
            total_local = q * v
            valor_total += total_local

            v_fmt = formatar_dinheiro_brl(v)
            t_fmt = formatar_dinheiro_brl(total_local)

            rows.append(
                "<tr>"
                f"<td>{item.get('numero','')}</td>"
                f"<td>{item.get('produto','')}</td>"
                f"<td>{(q)}</td>"
                f"<td>{item.get('unidade','')}</td>"
                f"<td>{v_fmt}</td>"
                f"<td>{t_fmt}</td>"
                "</tr>"
            )

        data['produtos']    = "".join(rows)
        data['valor_total'] = formatar_dinheiro_brl(valor_total)

    # 4) Injeta no HTML de placeholders
    # Template já em lowercase - sem conversão
    tpl_file = os.path.join('template-PDF', f"{template}_placeholders.html")
    if not os.path.exists(tpl_file):
        return jsonify({'erro': 'Template de placeholders não encontrado'}), 404

    html = open(tpl_file, encoding='utf-8').read()
    data['cnpj'] = formatar_cnpj(data['cnpj']) if len(data['cnpj']) == 14 else formatar_cpf(data['cnpj'])
    for k, v in data.items():
        
        html = html.replace(f"{{{k}}}", str(v))
    
    # 5) Gera PDF respeitando links estáticos
    base_url = os.path.abspath(os.getcwd())
    pdf_bytes = HTML(string=html, base_url=base_url).write_pdf()

    # 6) Retorna anexo
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = (
        f'attachment; filename=orcamento_{str(orcamento_id).zfill(3)}.pdf'
    )
    return response


def delete_orcamento(user_data, orcamento_id):
    """
    Remove um orçamento do sistema (bd/json_preenchimento e bd/edicoes).
    """
    from flask import jsonify

    print(f"[DEBUG] delete_orcamento called with ID: {orcamento_id}")
    print(f"[DEBUG] User: {user_data.get('user') if user_data else 'None'}")

    try:
        removed_files = []

        # Remove JSON base
        base_file = f"bd/json_preenchimento/{orcamento_id}.json"
        print(f"[DEBUG] Checking base file: {base_file}")
        if os.path.exists(base_file):
            os.remove(base_file)
            removed_files.append(base_file)
            print(f"[INFO] Removed base JSON: {base_file}")
        else:
            print(f"[DEBUG] Base file not found: {base_file}")

        # Remove todas as edições de templates
        templates_dir = "bd/edicoes"
        print(f"[DEBUG] Checking templates directory: {templates_dir}")
        if os.path.exists(templates_dir):
            template_dirs = os.listdir(templates_dir)
            print(f"[DEBUG] Found template directories: {template_dirs}")

            for template_dir in template_dirs:
                template_path = os.path.join(templates_dir, template_dir)
                if os.path.isdir(template_path):
                    edit_file = os.path.join(template_path, f"{orcamento_id}.json")
                    print(f"[DEBUG] Checking edit file: {edit_file}")
                    if os.path.exists(edit_file):
                        os.remove(edit_file)
                        removed_files.append(edit_file)
                        print(f"[INFO] Removed edit JSON: {edit_file}")
                    else:
                        print(f"[DEBUG] Edit file not found: {edit_file}")

        print(f"[DEBUG] Total files removed: {len(removed_files)}")
        print(f"[DEBUG] Removed files: {removed_files}")

        if removed_files:
            return jsonify({
                "mensagem": f"Orçamento {orcamento_id} removido com sucesso.",
                "arquivos_removidos": removed_files
            }), 200
        else:
            print(f"[WARNING] No files found for orçamento {orcamento_id}")
            return jsonify({"erro": f"Orçamento {orcamento_id} não encontrado."}), 404

    except Exception as e:
        print(f"[ERROR] Erro ao deletar orçamento {orcamento_id}: {str(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({"erro": f"Erro ao deletar orçamento: {str(e)}"}), 500


def orcamento(user_data):
    """
    Retorna todos os JSONs de orçamentos já preenchidos.
    """
    path     = "./bd/json_preenchimento"
    arquivos = [f for f in os.listdir(path) if f.endswith(".json")]
    todos    = []
    user    = user_data.get("user")
    data = get_data(user)
    for arquivo in arquivos:
        with open(os.path.join(path, arquivo), 'r', encoding='utf-8') as f:

            dados = json.load(f)
            print(dados["vendedor"])
            if dados["vendedor"] == data["nome"] or data["admin"]:
                todos.append(dados)
        
    return jsonify(todos), 200