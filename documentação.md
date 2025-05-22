# 📚 Documentação das Rotas da API

## 🔐 Autenticação

### `GET /`
Renderiza a página de login (`login.html`).

### `POST /login`
Realiza login com `username` e `password`. Retorna token de autenticação via cookie.

### `GET /logout`
Faz logout do usuário autenticado.

---

## 📊 Orçamentos

### `GET /preencher`
Renderiza a página de criação de orçamento (`geradorOrcamento.html`).

### `GET ou POST /postTemplate`
- `GET`: Renderiza o formulário de orçamento.
- `POST`: Recebe um JSON com os dados e salva o orçamento (gera ID e HTML de produtos).

### `GET /verification`
Renderiza a tela de revisão de templates de orçamento.

### `POST /verification/preview`
Gera uma prévia em HTML com os dados corrigidos para um determinado template.

### `POST /verification/update`
Atualiza um orçamento existente com novas informações (corrigidas).

### `GET /orçaemnto`
Retorna a lista de todos os orçamentos do usuário logado (ou todos, se admin).

### `DELETE /delete/<id>`
Remove o JSON de um orçamento com base no ID (de `json_preenchimento` e `edicoes`).

### `GET /download/<id>/<template>`
Gera e retorna um PDF do orçamento com base no ID e no template selecionado.

---

## 👤 Usuários

### `GET /dashboard`
Renderiza a dashboard principal com botões de ação (cadastrar, criar orçamento, etc).

### `GET /cadastro`
Renderiza a tela de cadastro de usuário (`cadastro_usuario.html`).

### `POST /add_usuario`
Adiciona um novo usuário. Requer privilégio de administrador.

### `GET /usuario`
Retorna uma lista de todos os usuários cadastrados.

### `DELETE /delete_usuario/<username>`
Exclui um usuário com base no nome. Remove arquivo e entrada em `funcionarios.json`.

### `GET /user`
Retorna os dados básicos do usuário logado.

---

## 👥 Clientes

### `GET /p_cadastro_cliente`
Renderiza a página de cadastro de clientes (`cadastro_cliente.html`).

### `POST /cadastra_cliente`
Cadastra um novo cliente com base no CNPJ. Salva arquivo JSON em `bd/clientes`.

### `GET /get_cliente`
Retorna uma lista com todos os clientes cadastrados.

---

## 📂 Arquivos e Recursos

### `GET /static/<filename>`
Serve arquivos estáticos com CORS liberado.

### `GET /template-PDF/<filename>`
Serve templates HTML diretamente da pasta `template-PDF`.

### `GET /getTemplate`
Retorna o PDF `orcamento.pdf` como anexo (pré-gerado).

### `GET /impressao?arquivo=...`
Lê um template HTML e o exibe com o CNPJ formatado.

---

## 🛠️ Outros

### `GET /dev_god`
Retorna o nome dos desenvolvedores.

---

## 🔄 Pós-Resposta

### `after_request`
Adiciona cabeçalhos CORS adicionais após cada resposta.

---
