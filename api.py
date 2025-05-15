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

app = Flask(__name__)
# Permite carregar templates também de template-PDF
app.jinja_loader = ChoiceLoader([
    FileSystemLoader('./template-PDF'),
    app.jinja_loader,
])

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
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
    token = logon(auth.get("username"), auth.get("password"), app.config['SECRET_KEY'])["token"]
    if not isinstance(token, str):
        return jsonify({'messagem':'erro ao logar'}), 401
    response = make_response(jsonify({'message':'Login bem-sucedido','user':auth.get("username")}))
    response.set_cookie(
        'auth_token', token,
        httponly=True, secure=True, samesite='Strict', max_age=360000#em segundos 10 horas
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
@token_required
def receber_orcamento(user_data):
    if request.method == 'GET':
        return render_template("geradorOrcamento.html")
    dados = request.get_json(force=True)
    # converte produtos em HTML
    itens = dados.get("produtos", [])
    html_rows = ''.join(
        f"<tr><td>{i['numero']}</td><td>{i['produto']}</td>"
        f"<td>{i['quantidade']}</td><td>{i['unidade']}</td>"
        f"<td>{i['valor_unitario']}</td><td>{i['total_local']}</td></tr>"
        for i in itens
    )
    dados["produtos"] = html_rows

    # salva JSON incremental
    pasta = "bd/json_preenchimento"
    os.makedirs(pasta, exist_ok=True)
    files = [f for f in os.listdir(pasta) if f.endswith('.json')]
    ids = [int(f.split('.')[0]) for f in files if f.split('.')[0].isdigit()]
    nid = max(ids)+1 if ids else 1
    path = os.path.join(pasta, f"{nid}.json")
    nome     = user_data.get("nome")
    dados_funcionario = get_data(nome)
    dados["vendedor"] = dados_funcionario.get("nome")
    dados["id"]=nid

    with open(path,'w',encoding='utf-8') as f:
        json.dump(dados,f,indent=2,ensure_ascii=False)
    # gera HTMLs iniciais para cada template
    tpl_dir = 'template-PDF'
    os.makedirs(tpl_dir,exist_ok=True)
    templates = dados.get('templates',[])
    if isinstance(templates,str): templates=[templates]
    for emp in templates:
        tpl_file = os.path.join(tpl_dir, f"{emp.lower()}_placeholders.html")
        if not os.path.exists(tpl_file): continue
        tpl_html = open(tpl_file,encoding='utf-8').read()
        for k,v in dados.items(): tpl_html = tpl_html.replace(f"{{{k}}}", str(v))
        out_name = f"orcamento_{str(nid).zfill(3)}_{emp.lower()}.html"
        with open(os.path.join(tpl_dir,out_name),'w',encoding='utf-8') as f:
            f.write(tpl_html)
    return jsonify({"mensagem":f"Orçamentos salvos para {', '.join(templates)}."}),200

@app.route("/verification", methods=["GET"])
def verificar_template():
    json_dir = "bd/json_preenchimento"
    arquivos = sorted(
        [f for f in os.listdir(json_dir) if f.endswith('.json')],
        key=lambda f: os.path.getmtime(os.path.join(json_dir,f))
    )
    if not arquivos:
        return "Nenhum JSON encontrado",404
    json_file = request.args.get('json_file', arquivos[-1])
    if json_file not in arquivos: json_file = arquivos[-1]
    dados = json.load(open(os.path.join(json_dir,json_file),'r',encoding='utf-8'))
    # converte produtos
    raw = dados.get('produtos','')
    if isinstance(raw,str):
        lst=[]
        for trecho in raw.split('</tr>'):
            if '<tr>' not in trecho: continue
            cells = re.findall(r'<td>(.*?)</td>', trecho, flags=re.DOTALL)
            lst.append({
                'numero':cells[0] if len(cells)>0 else '',
                'produto':cells[1] if len(cells)>1 else '',
                'quantidade':cells[2] if len(cells)>2 else '',
                'unidade':cells[3] if len(cells)>3 else '',
                'valor_unitario':cells[4] if len(cells)>4 else '',
                'total_local':cells[5] if len(cells)>5 else ''
            })
        dados['produtos']=lst
    templates = dados.get('templates',[])
    if isinstance(templates,str): templates=[templates]
    idx = int(request.args.get('template_idx',0) or 0)
    if idx>=len(templates):
        return ("<h2>Todos os templates foram revisados!</h2><a href='/dashboard'>Voltar para Início</a>",200)
    emp = templates[idx]
    # usa id do json_file
    base_id = int(json_file.split('.')[0])
    iframe_src = f"/template-PDF/orcamento_{str(base_id).zfill(3)}_{emp.lower()}.html"
    return render_template('revisao.html', iframe_src=iframe_src,
                           template_nome=emp, proximo_idx=idx+1,
                           dados=dados, json_filename=json_file,id=base_id), 200

@app.route("/verification/preview", methods=["POST"])
def preview_template():
    correcoes = request.get_json(force=True)
    tpl = correcoes.get('template')
    # load original
    dirj = 'bd/json_preenchimento'
    files = sorted([f for f in os.listdir(dirj) if f.endswith('.json')],
                   key=lambda f: os.path.getmtime(os.path.join(dirj,f)))
    jf = correcoes.get('json_file', files[-1])
    orig = json.load(open(os.path.join(dirj,jf),'r',encoding='utf-8'))
    novo = orig.copy(); novo['templates']=[tpl]
    for k,v in correcoes.items():
        if k not in ('template','json_file'): novo[k]=v
    # convert produtos list to rows
    if isinstance(novo.get('produtos'), list):
        rows = []
        for item in novo['produtos']:
            rows.append(
                '<tr>' +
                ''.join(f'<td>{item.get(fld,"")}</td>' for fld in ['numero','produto','quantidade','unidade','valor_unitario','total_local']) +
                '</tr>'
            )
        novo['produtos'] = ''.join(rows)
    # inject
    tpl_path = os.path.join('template-PDF', f"{tpl.lower()}_placeholders.html")
    html = open(tpl_path,encoding='utf-8').read()
    for k,v in novo.items(): html = html.replace(f"{{{k}}}", str(v))
    html = html.replace('href="/css/','href="'+url_for('static', filename='css/') )
    html = html.replace('src="/img/','src="'+url_for('static', filename='img/') )
    return jsonify({'preview_html':html}),200

@app.route("/verification/update", methods=["POST"])
def update_template():
    try:
        correcoes = request.get_json(force=True)
        tpl = correcoes.get('template')
        jf  = correcoes.get('json_file')
        dirj= 'bd/json_preenchimento'
        orig= json.load(open(os.path.join(dirj,jf),'r',encoding='utf-8'))
        base_id = int(jf.split('.')[0])
        novo = orig.copy(); novo['templates']=[tpl]
        for k,v in correcoes.items():
            if k not in ('template','json_file'): novo[k]=v
        # detect change        
        use_id = base_id
        # generate html
        itens = novo.get("produtos", [])
        html_rows = ''.join(
        f"<tr><td>{i['numero']}</td><td>{i['produto']}</td>"
        f"<td>{i['quantidade']}</td><td>{i['unidade']}</td>"
        f"<td>R$ {i['valor_unitario']}</td><td>R$ {i['total_local']}</td></tr>"
        for i in itens
         )
        novo["produtos"] = html_rows
        tpl_file = f"{tpl.lower()}_placeholders.html"
        html = open(os.path.join('template-PDF',tpl_file),encoding='utf-8').read()
        for k,v in novo.items(): html = html.replace(f"{{{k}}}",str(v))
        html = html.replace('href="/css/','href="/static/css/')
        html = html.replace('src="/img/','src="/static/img/')
        out = f"orcamento_{str(use_id).zfill(3)}_{tpl.lower()}.html"
        with open(os.path.join('template-PDF',out),'w',encoding='utf-8') as f: f.write(html)
        return jsonify({'new_iframe_src':f"/template-PDF/{out}"}),200
    except Exception as e:
        return jsonify({'erro':str(e)}),500

@app.route("/download/<id>/<template>", methods=["GET"])
def download(id, template):
    """
    Renderiza a página de download com o iframe contendo o orçamento
    """
    print(f"Download solicitado: id={id}, template={template}")
    # Gera o nome do arquivo do template
    template_nome = f"/orcamento_{str(id).zfill(3)}_{template.lower()}.html"
    
    rendered_html = render_template(template_nome)
    pdf = HTML(string=rendered_html).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=orcamento.pdf'
    return response

@app.route('/impressao', methods=['GET'])
def imprimir_template():
    arquivo = request.args.get('arquivo')
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
    if dados.get("admin"):
        btn = "<input type='text' class='search' placeholder='Buscar...'  oninput='filtrarOrcamentos(this.value)'><button class='btn' onclick='novoOrcamento()'>gerar novo orçamento</button> <button class='btn' onclick='novoFuncionario()'>cadastra empregado</button>"
    else:
        btn = "<input type='text' class='search' placeholder='Buscar...' oninput='filtrarOrcamentos(this.value)'><button class='btn' onclick='novoOrcamento()'>gerar novo orçamento</button>"
    return render_template('index.html', info=info,btns=btn), 200


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
    nome = get_data(nome)["nome"]
    for arquivo in arquivos:
        with open(os.path.join(path, arquivo), 'r', encoding='utf-8') as f:

            dados = json.load(f)
            print(dados["vendedor"])
            if dados["vendedor"] == nome:
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


@app.after_request
def after_request(response):
    """
    Ajusta cabeçalhos CORS adicionais após cada resposta.
    """
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-access-token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


@app.route("/delete_usuario/<username>", methods=['DELETE'])
@token_required
def delete_usuario(user_data, username):
    BASE_DIR = os.path.dirname(__file__)
    BD_DIR = os.path.join(BASE_DIR, 'bd')
    USERS_DIR = os.path.join(BD_DIR, 'funcionarios')       # pasta com os arquivos {username}.json
    LIST_FILE = os.path.join(BD_DIR, 'funcionarios.json')
    """
    Exclui o arquivo bd/funcionarios/{username}.json
    Remove a chave username do JSON em bd/funcionarios.json
    """
    user_file = os.path.join(USERS_DIR, f"{username}.json")

    
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

@app.route("/dev_god", methods=['GET'])
def dev_god():
    return "Bernardo Ribeiro , Caio Ferreira , Ricardo Bandeira",200
def get_data(nome):
    path = os.path.join('bd/funcionarios', f"{nome}.json")
    with open(path, 'r', encoding='utf-8') as f:
        dados = json.load(f)
   
    return dados
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)