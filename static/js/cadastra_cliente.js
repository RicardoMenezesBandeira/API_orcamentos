window.onload = function() {
    clientes();

};
lista_clientes = []
let url = window.location.origin
function clientes(){
    
    fetch(url+'/get_cliente', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (response.status === 200) {
            return response.json();
        } else {
            throw new Error('Erro ao buscar os dados do cliente');
        }
    })
    .then(data => {
        console.log('Dados do cliente:', data);
        clientes = document.getElementById('clientes');
        line = "";
        lista_clientes = data
        data.forEach(element => {
            line +=  "<li class='list-group-item list-group-item-action' onclick='seleciona(" + element.cnpj+ ")'>" +
      "<div>Cliente: " + element.cliente + "</div>" +
      "<div>CNPJ: " + formatarCNPJ(element.cnpj) + "</div>" +
      "<div>Nome fantasia: " + element.nome + "</div>" +
      "</li>";
        });
        clientes.innerHTML = line;
    })
    .catch(error => {
        console.error('Erro na requisição:', error);
    });
}

function filtrarPorCNPJ(valor) {
    clientes = document.getElementById('clientes');
    console.log(valor)

  // Filtra a lista original com base no CNPJ digitado
  const resultados = lista_clientes.filter(element =>
    element.cnpj && element.cnpj.toString().startsWith(valor)
  );
  lista = "";
  resultados.forEach(element => {
    lista += "<li class='list-group-item list-group-item-action' onclick='seleciona(" + element.cnpj+ ")'>" +
      "<div>Cliente: " + element.cliente + "</div>" +
      "<div>CNPJ: " + formatarCNPJ(element.cnpj) + "</div>" +
      "<div>Nome fantasia: " + element.nome + "</div>" +
      "</li>";
  });
 
        clientes.innerHTML = lista;
   
  
}
function seleciona(cnpj) {
    lista_clientes.forEach(element => {
        if (element.cnpj == cnpj) {
            console.log(element)
            preencheFormulario(element);
        }
    }
    )
}
function formatarCNPJ(cnpj) {
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, "$1.$2.$3/$4-$5");
}

function preencheFormulario(cliente) {
    form = document.querySelector('.form-grid');
        Object.entries(cliente).forEach(([key, value]) => {
    const input = form.querySelector(`[name="${key}"]`);
    if (input) input.value = value;


    })}
function Cadastra_cliente() {
    const inputs = document.querySelectorAll('.form-grid input');
    data={}
    inputs.forEach(input => {        
        data[input.name]= input.value
    });
    data['cnpj'] = data['cnpj'].replace(/\D/g, ''); // Remove caracteres não numéricos
    console.log(data)
    fetch(url+'/cadastra_cliente', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(data)
    }).then(response => {
        if (response.status === 200) {
            mostrarMensagem('sucesso', 'Cliente salvo com sucesso!');

        } else {
            mostrarMensagem('erro', 'Erro ao cadastrar o cliente');

            
        }
    })

}

function voltar() {
    window.location.href = "/dashboard";
}

function mostrarMensagem(tipo, texto) {
  const msg = document.getElementById("mensagem-flash");
  msg.textContent = texto;
  msg.className = `alerta ${tipo}`; // aplica 'sucesso' ou 'erro'
  msg.style.display = "block";

  // Remove com fade-out após 4.5s
  setTimeout(() => {
    msg.classList.add("fade-out");
  }, 4500);

  // Esconde totalmente após 5s
  setTimeout(() => {
    msg.style.display = "none";
    msg.classList.remove("fade-out");
  }, 5000);
}s