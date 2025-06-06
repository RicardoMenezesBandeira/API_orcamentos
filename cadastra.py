import json
import os
def cadastrar(data):
    
    usuario = {
    "nome": data["nome"],
    "telefone":data["telefone"],
    "user":data["user"],
    "admin":data["admin"]
}
    login = {
    "user": data["user"],
    "senha": data["senha"]
    }
    print(usuario) 
    print(login)
    try:
        # Diretório onde o arquivo será salvo
        diretorio = f'./bd/funcionarios/'

        # Verifica se o diretório existe, se não, cria
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)

        with open(f'./bd/funcionarios/{login["user"]}.json', 'w', encoding='utf-8') as f:
            json.dump(usuario, f, indent=4, ensure_ascii=False)
        # Tenta carregar a lista de funcionários, se o arquivo não existir ou estiver vazio, cria uma lista vazia
        try:
            with open(f'./bd/funcionarios.json', 'r', encoding='utf-8') as f:
                funcionarios = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):  # Se não encontrar o arquivo ou estiver vazio
            funcionarios = []
        
        # Adiciona o novo usuário à lista de funcionários
        user = login["user"]
        print(funcionarios)
        if user in funcionarios:
            print("Usuario já existe")
        else:
            print ("Usuario não existe")
            senha = login["senha"]        
            funcionarios[user] = {"senha":senha}
        # Salva a lista atualizada de funcionários
        with open(f'./bd/funcionarios.json', 'w', encoding='utf-8') as f:
            json.dump(funcionarios, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao cadastrar usuário: {str(e)}")
        return {"erro": str(e)}, 500
    return True
if __name__ == "__main__":
    dados= {'nome': 'gabryellla Nata', 'user': 'bibi', 'telefone': '22999058942', 'senha': '1234'}
    cadastrar(dados)