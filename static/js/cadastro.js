const formCadastro = document.getElementById('form-cadastro');
const listaUsuarios = document.getElementById('lista-usuarios');
let usuarios = [];
let url = window.location.origin;
function renderizarUsuarios() {
  listaUsuarios.innerHTML = '';
  usuarios.forEach((usuario, index) => {
    const li = document.createElement('li');
    li.className = 'list-group-item d-flex justify-content-between align-items-center';
    li.innerHTML = `
      ${usuario.nome} (${usuario.user})
      <div>
        <button class="btn btn-sm btn-danger" onclick="excluirUsuario(${index})">Excluir</button>
      </div>
    `;
    listaUsuarios.appendChild(li);
  });
}

formCadastro.addEventListener('submit', function(event) {
  event.preventDefault();
  const nome = document.getElementById('nome').value;
  const user = document.getElementById('user').value;
  const telefone = document.getElementById('telefone').value;
  const senha = document.getElementById('senha').value;
  const admin = document.getElementById('admin').checked; // Verifica se o checkbox está marcado

  const dados = { nome, user, telefone, senha ,admin}; // Monta o JSON

  // Envia o JSON para o servidor
  fetch(url+'/add_usuario', {
    method: 'POST', // método POST para enviar dados
    headers: {
      'Content-Type': 'application/json',
      credentials: 'include' // indica que está mandando JSON
    },
    body: JSON.stringify(dados), // transforma o objeto em JSON string
     credentials: 'include'
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
  
    if(data.message == "Acesso não autorizado!")
      return alert('Cadastro não autorizado!');
    console.log('Sucesso:', data);
    usuarios.push(dados); // Opcional: adiciona na lista local também
    renderizarUsuarios();
    formCadastro.reset();
  })
  .catch((error) => {
    console.error('Erro:', error);
  });

});

async function excluirUsuario(index) {
  if (confirm('Tem certeza que deseja excluir este usuário?')) {
    username = usuarios[index].user;
    try {
      const response = await fetch(url+`/delete_usuario/${encodeURIComponent(username)}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Erro desconhecido');
      }

      // remove do array local e re-renderiza
      alert(`Usuário "${username}" excluído com sucesso!`);
      usuarios.splice(index, 1);
      renderizarUsuarios();
    } catch (error) {
      alert(`Falha ao excluir usuário: ${error.message}`);
      console.error(error);
    }
  }
   
  }


function editarUsuario(index) {
  const usuario = usuarios[index];
  document.getElementById('nome').value = usuario.nome;
  document.getElementById('user').value = usuario.user;
  document.getElementById('telefone').value = usuario.telefone;
  document.getElementById('senha').value = usuario.senha;

  usuarios.splice(index, 1);
  renderizarUsuarios();
}
window.onload = function() {
  fetch(url+'/usuario')  // faz uma requisição para o endpoint /usuarios
  .then(response => response.json())  // converte a resposta para JSON
  .then(data => {
    console.log(data)
    usuarios=data;  // atribui os dados recebidos à variável usuarios
    renderizarUsuarios();  // renderiza a lista de usuários
  })
  .catch(error => {
    console.error('Erro ao buscar o JSON:', error);
  });
}