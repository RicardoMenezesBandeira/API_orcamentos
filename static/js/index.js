  
  function novoOrcamento(){
    // Redireciona para a página principal
    window.location.href = "/preencher";
  }
  function novoFuncionario(){
    // Redireciona para a página principal
    window.location.href = "/cadastro";
  }function atualizaOrcamento(){
    fetch('/orçaemnto', {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/json',
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Erro na requisição: ' + response.status);
      }
      return response.json(); // Aqui você converte pra JSON
    })
    .then(dados => { // Agora sim os dados estão prontos
      console.log('Dados recebidos:', dados);
      let orca = document.getElementById("orcamento");
      let lista = "<table class='table'><tbody>";
      let id = 0;
      dados.forEach(function(dado) {
        console.log(dado); // Verifica o que está vindo
        let templates = dado.templates || []; // Garante que seja uma lista

        let circulos = '';
        const tipos = ['BossBR', 'Bling', 'PCasallas','construcom']; // os nomes que você quer verificar

        tipos.forEach(tipo => {
          if (templates.includes(tipo)) {
            circulos += "<td>🔵</td>"; // Círculo preenchido se existir
          } else {
            circulos += "<td>⚪</td> "; // Círculo vazio se não existir
          }
        });
        lista += "<tr class='row'>" +
             "<td>" + dado.id + "</td>" +
             circulos +
             // botão vermelho (danger)
             "<td><button class='btn btn-danger btn-sm' onclick='download(" + id + ")'>Download</button></td>" +
           "</tr>";
        id++;
      });
      lista += "</tbody></table>";

      orca.innerHTML = lista;

    })
    .catch(error => {
      console.error('Erro ao buscar os dados:', error);
    });
  }
  
  
  window.onload = function() {
    atualizaOrcamento();
  }
