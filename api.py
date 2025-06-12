from flask import Flask, request, jsonify, redirect, render_template, send_file, send_from_directory, url_for, make_response, session
from jinja2 import ChoiceLoader, FileSystemLoader
from werkzeug.utils import secure_filename  # sanitiza nomes de arquivos
from flask_cors import CORS
import os
import json
import re
from login import token_required, clean_tolkens, create_token, logon,logout
from cadastra import cadastrar
from functools import wraps
from weasyprint import HTML
from babel.numbers import format_currency

def formatar_dinheiro_brl(valor: float, casas: int = 4) -> str:
    fmt = '¤#,##0.' + '0' * casas
    return format_currency(valor, 'BRL', locale='pt_BR', format=fmt)

def formatar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', cnpj)  # Remove tudo que não for dígito
    return re.sub(r'^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$', r'\1.\2.\3/\4-\5', cnpj)
def formatar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)  # Remove tudo que não for dígito
    return re.sub(r'^(\d{3})(\d{3})(\d{3})(\d{2})$', r'\1.\2.\3-\4', cpf)

app = Flask(__name__)
# Permite carregar templates também de template-PDF
app.jinja_loader = ChoiceLoader([
    FileSystemLoader('./template-PDF'),
    app.jinja_loader,
])

# Aplica CORS com função personalizada
CORS(app,  supports_credentials=True)
app.config['SECRET_KEY'] = 'meusegredosecreto'

# Serve arquivos estáticos com CORS
@app.route('/static/<path:filename>')
def serve_static(filename):
    response = send_from_directory('static', filename)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route("/")
def login_page():
    return render_template('login.html')

@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    token =logon(auth.get("username"), auth.get("password"), app.config['SECRET_KEY'])["token"]
    if token == "erro":
        return jsonify({'message': 'Usuário ou senha inválidos!'}), 401
    response = make_response(jsonify({'message':'Login bem-sucedido','user':auth.get("username")}))
    response.set_cookie(
        'auth_token', token,
        httponly=True, secure=False, samesite='Lax'
    )
    return response

@app.route("/logout",methods=["GET"])
@token_required
def logout_route(user_data):
    print("Logout solicitado")
    if logout() == True:    
        print("Logout bem-sucedido")
        return jsonify({"message":"Logout bem-sucedido!"}), 200
    else:
        print("Erro ao fazer logout")
        return jsonify({"message":"Erro ao fazer logout!"}), 500

@app.route("/preencher")
@token_required
def preencher(user_data):
    return render_template("geradorOrcamento.html")

@app.route("/postTemplate", methods=['GET','POST'])
@token_required  # presume decorator definido em outro lugar
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
    nome_user = user_data.get("nome")
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

@app.route("/verification", methods=["GET"])
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

def parse_valor_brasileiro(valor):
    if not valor:
        return 0.0
    valor = str(valor).replace('.', '').replace(',', '.')
    try:
        return float(valor)
    except ValueError:
        return 0.0


@app.route("/verification/preview", methods=["POST"])
@token_required
def preview_template(user_data):
    import traceback

    print(f"[INFO] preview_template called by user: {user_data.get('nome')}")
    correcoes = request.get_json(force=True)
    print(f"[DEBUG] Correções recebidas keys: {list(correcoes.keys())}")
    tpl       = correcoes.get('template')
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
                q = parse_valor_brasileiro(item.get('quantidade'))
                v = parse_valor_brasileiro(item.get('valor_unitario'))
                print(f"[DEBUG] Processing item: {item.get('numero')} - {item.get('produto')} - Q: {q}, V: {v}")
                total = q * v
                valor_total += total
                rows.append(
                    '<tr class="nao-quebrar">'
                    f'<td>{item.get("numero")}</td>'
                    f'<td>{item.get("produto")}</td>'
                    f'<td>{q}</td>'
                    f'<td>{item.get("unidade")}</td>'
                    f'<td>{format_currency(v, "BRL", locale="pt_BR", format="¤#,##0.0000")}</td>'
                    f'<td>{format_currency(total, "BRL", locale="pt_BR", format="¤#,##0.0000")}</td>'
                    '</tr>'
                )
            novo['produtos']    = ''.join(rows)
            novo['valor_total'] = format_currency(valor_total, "BRL", locale="pt_BR", format="¤#,##0.0000")
            print(f"[DEBUG] Reconstrução de produtos OK")
        except Exception as e:
            print(f"[ERROR] Falha ao reconstruir produtos: {e}")
            traceback.print_exc()
    else:
        print("[DEBUG] Produto permanece como string HTML (não era lista)")

    # 6) Injeta no template e retorna HTML
    placeholder = os.path.join('template-PDF', f"{tpl.lower()}_placeholders.html")
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

@app.route("/verification/update", methods=["POST"])
@token_required
def atualiza_orcamento(user_data):
    print(f"[INFO] atualiza_orcamento called by user: {user_data.get('nome')}")
    correcoes = request.get_json(force=True)
    tpl = correcoes.get('template')
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
    placeholder_file = os.path.join(tpl_dir, f"{tpl.lower()}_placeholders.html")
    if not os.path.exists(placeholder_file):
        print(f"[WARNING] Placeholder file not found: {placeholder_file}")

    return jsonify({"mensagem": f"Template '{tpl}' atualizado e salvo."}), 200


@app.route('/download/<int:orcamento_id>/<template>', methods=['GET'])
@token_required
def download_orcamento(user_data, orcamento_id, template):
    tpl_lower = template.lower()
    
    # 1) Monta paths possíveis
    path_edicoes = os.path.join('bd', 'edicoes', template, f'{orcamento_id}.json')
    path_base    = os.path.join('bd', 'json_preenchimento', f'{orcamento_id}.json')
    if os.path.exists(path_edicoes):
        print(f"[DEBUG] Found edited JSON at {path_edicoes}")
        json_path = path_edicoes
    elif os.path.exists(path_base):
        print(f"[DEBUG] NOT Found edited JSON at {path_edicoes}")
        json_path = path_base
    else:
        return jsonify({'erro': 'JSON não encontrado em edicoes nem em json_preenchimento'}), 404

    # 2) Carrega JSON
    print("[DEBUG] Loading JSON from", json_path)
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    print("[DEBUG] JSON loaded successfully")

    # 3) Converte lista de produtos em HTML + calcula valor_total
    produtos = data.get('produtos')
    if isinstance(produtos, list):
        rows = []
        valor_total = 0.0
        for item in produtos:
            q = parse_valor_brasileiro(item.get('quantidade'))
            v = parse_valor_brasileiro(item.get('valor_unitario'))
            print(f"[DEBUG] Processing item: {item.get('numero')} - {item.get('produto')} - Q: {q}, V: {v}")
            total_local = q * v
            valor_total += total_local

            v_fmt = format_currency(v, "BRL", locale="pt_BR", format="¤#,##0.0000")
            t_fmt = format_currency(total_local, "BRL", locale="pt_BR", format="¤#,##0.0000")

            rows.append(
                '<tr class="nao-quebrar">'
                f"<td>{item.get('numero','')}</td>"
                f"<td>{item.get('produto','')}</td>"
                f"<td>{int(q)}</td>"
                f"<td>{item.get('unidade','')}</td>"
                f"<td>{v_fmt}</td>"
                f"<td>{t_fmt}</td>"
                "</tr>"
            )

        data['produtos']    = "".join(rows)
        data['valor_total'] = format_currency(valor_total, "BRL", locale="pt_BR", format="¤#,##0.0000")

    # 4) Injeta no HTML de placeholders
    tpl_file = os.path.join('template-PDF', f"{tpl_lower}_placeholders.html")
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

@app.route('/impressao', methods=['GET'])
def imprimir_template():
    arquivo = request.args.get('arquivo')
    arquivo["cnpj"] = formatar_cnpj(arquivo["cnpj"])
    html = open(os.path.join('template-PDF',arquivo),'r',encoding='utf-8').read()
    return render_template(html),200

@app.route("/template-PDF/<path:filename>")
def servir_template_pdf(filename):
    return send_from_directory("template-PDF", filename)


@app.route("/dashboard", methods=['GET'])
@token_required
def get_dashboard(user_data):
    
    nome     = user_data.get("nome")
    dados =get_data(nome)
    nome = dados.get("nome")
    info     = f"Nome: {nome}"
    btn = "<button class='btn' onclick='novoOrcamento()'>gerar novo orçamento</button>"
    if dados.get("admin"):
        btn += " <button class='btn' onclick='novoFuncionario()'>cadastra empregado</button>"

    return render_template('index.html', info=info, btns=btn), 200

@app.route("/orçaemnto", methods=['GET'])
@token_required
def orcamento(user_data):
    """
    Retorna todos os JSONs de orçamentos já preenchidos.
    """
    path     = "./bd/json_preenchimento"
    arquivos = [f for f in os.listdir(path) if f.endswith(".json")]
    todos    = []
    nome    = user_data.get("nome")
    nome = get_data(nome)
    for arquivo in arquivos:
        with open(os.path.join(path, arquivo), 'r', encoding='utf-8') as f:

            dados = json.load(f)
            print(dados["vendedor"])
            if dados["vendedor"] == nome["nome"] or nome["admin"]:
                todos.append(dados)
        
    return jsonify(todos), 200

@app.route("/user", methods=['GET'])
@token_required
def user(user_data):
    nome     = user_data.get("nome")
    dados =get_data(nome)
    nome = dados.get("nome")   
    return jsonify(nome), 200

@app.route("/getTemplate", methods=['POST'])
def get_template():
    """
    Envia um PDF pré-gerado como anexo.
    """
    # OPTIONS já liberado globalmente pelo CORS
    return send_file('orcamento.pdf', as_attachment=True)

@app.route('/delete/<id>', methods=['DELETE'])# ajeitar para deletar os #
@token_required
def delete_orcamento(user_data, id):
    """
    Deleta o arquivo de orçamento correspondente ao ID.
    """
    path = "bd/json_preenchimento"
    path2 = "bd/edicoes"
    pastas = ["PCasallas", "BossBR","Construcom","Big"]

    file_path = os.path.join(path, f"{id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    for pasta in pastas:
        file_path = os.path.join(path2, pasta, f"{id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
       
    else:
        return jsonify({"message": "Arquivo não encontrado!"}), 404

@app.route("/cadastro")
@token_required
def cadastro_page(user_data):
    """
    Exibe o formulário de cadastro de novos usuários.
    """
    return render_template('cadastro_usuario.html')


@app.route("/add_usuario", methods=['POST'])
@token_required
def add_usuario(user_data):
    """
    Recebe JSON com dados de usuário e chama a função cadastrar().
    """
    dados = get_data(user_data.get("nome"))
    permision = dados.get("admin")
    if not permision:
        return jsonify({"message": "Acesso não autorizado!"}), 401 # Não mudar esta mensagem, pois o front-end depende dela.
    data = request.get_json(force=True)
    success = cadastrar(data)
    if success:
        return jsonify({"message": "Usuário adicionado com sucesso!"}), 200
    else:
        return jsonify({"message": "Erro ao adicionar usuário!"}), 500


@app.route("/usuario", methods=['GET'])
@token_required
def usuario_page(user_data):
    """
    Lê todos os arquivos JSON em bd/funcionarios e retorna como lista.
    """
    diretorio   = './bd/funcionarios'
    todos_os_dados = []
    for nome_arquivo in os.listdir(diretorio):
        if nome_arquivo.endswith('.json'):
            with open(os.path.join(diretorio, nome_arquivo), 'r', encoding='utf-8') as f:
                dados = json.load(f)
                todos_os_dados.append(dados)
    return jsonify(todos_os_dados), 200

@app.route("/delete_usuario/<username>", methods=['DELETE'])
@token_required
def delete_usuario(user_data, username):
    user = get_data(user_data.get("nome"))
    name = user.get("user")
    username = username.lower()
    if name == username:
        return jsonify({"error": "Você não pode excluir a si mesmo!"}),401

    BASE_DIR = os.path.dirname(__file__)
    BD_DIR = os.path.join(BASE_DIR, 'bd')
    USERS_DIR = os.path.join(BD_DIR, 'funcionarios')       # pasta com os arquivos {username}.json
    LIST_FILE = os.path.join(BD_DIR, 'funcionarios.json')
    """
    Exclui o arquivo bd/funcionarios/{username}.json
    Remove a chave username do JSON em bd/funcionarios.json
    """
    user_file = os.path.join(USERS_DIR, f"{username}.json")
    print(f"Tentando deletar o arquivo: {user_file}") # DEBUG
    print(f"O arquivo existe? {os.path.exists(user_file)}") # DEBUG
    
    try:
        os.remove(user_file)
    except FileNotFoundError:
        return jsonify({"error": f"Arquivo do usuário '{username}' não encontrado."}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao apagar arquivo de usuário."}), 500

    try:
        with open(LIST_FILE, 'r', encoding='utf-8') as f:
            all_users = json.load(f)

        if username not in all_users:
            return jsonify({"error": f"Usuário '{username}' não encontrado na lista."}), 404

        del all_users[username]

        with open(LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_users, f, ensure_ascii=False, indent=2)

        return jsonify({"message": f"Usuário '{username}' excluído com sucesso."}), 200

    except FileNotFoundError:
        return jsonify({"error": "Arquivo de lista de usuários não encontrado."}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "JSON de lista de usuários inválido."}), 500
    except Exception as e:
        return jsonify({"error": "Erro ao atualizar lista de usuários."}), 500

@app.route("/p_cadastro_cliente")
@token_required
def p_cadastro_cliente(user_data):   
    return render_template('cadastro_cliente.html'), 200

@app.route("/cadastra_cliente", methods=['POST'])
@token_required
def cadastra_cliente(user_data):   
    dados  = request.get_json()
    print(dados)
    cliente = dados
    cnpj = dados['cnpj']
    print(cnpj)
    if not cnpj:
        return jsonify({"message": "CNPJ não fornecido!"}), 400
    
    path= "bd/clientes"
    os.makedirs(path, exist_ok=True)
    path = os.path.join(path, f"{cnpj}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cliente, f, indent=2, ensure_ascii=False)
    return jsonify({"message": "Cliente cadastrado com sucesso!"}), 200

@app.route("/get_cliente", methods=['GET'])
@token_required
def get_cliente(user_data):
    diretorio   = './bd/clientes'
    todos_os_dados = []
    for nome_arquivo in os.listdir(diretorio):
        if nome_arquivo.endswith('.json'):
            with open(os.path.join(diretorio, nome_arquivo), 'r', encoding='utf-8') as f:
                dados = json.load(f)
                todos_os_dados.append(dados)
    return jsonify(todos_os_dados), 200

@app.route('/delete_cliente/<cnpj>', methods=['DELETE'])
@token_required
def delete_cliente(cnpj, user_data):
    try:
        clientes_path = f'bd/clientes/{cnpj}.json'

        if not os.path.exists(clientes_path):
            return jsonify({'message': 'Arquivo de clientes não encontrado'}), 404

        os.remove(clientes_path)
        return jsonify({'message': 'Cliente deletado com sucesso'}), 200

    except Exception as e:
        return jsonify({'message': f'Erro ao deletar cliente: {str(e)}'}), 500

@app.route("/dev_god", methods=['GET'])
def dev_god():
    return "Bernardo Ribeiro , Caio Ferreira , Ricardo Bandeira",200

def get_data(nome):
    path = os.path.join('bd/funcionarios', f"{nome}.json")
    with open(path, 'r', encoding='utf-8') as f:
        dados = json.load(f)
   
    return dados
@app.route("/logout_all")
def logout_all():
    clean_tolkens()  # Limpa todos os tokens armazenados
    print("Todos os tokens foram limpos da memória.")
    return jsonify({"message": "Todos os tokens foram invalidados."}), 200

@app.after_request
def after_request(response):
    """
    Ajusta cabeçalhos CORS adicionais após cada resposta.
    """
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-access-token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)