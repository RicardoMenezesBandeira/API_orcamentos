  let orcamento  = []
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
      orcamento =  dados;
      let orca = document.getElementById("orcamento");
      let lista = "<table class='table'><tbody>";
      let id = 1;
      dados.forEach(function(dado) {
        console.log(dado); // Verifica o que está vindo
        let templates = dado.templates || []; // Garante que seja uma lista

        let circulos = '';
        const tipos = ['BossBR', 'PCasallas','Construcom']; // os nomes que você quer verificar

        tipos.forEach(tipo => {
          if (templates.includes(tipo)) {
            circulos += `<td><button class='btn btn-danger btn-sm' onclick='download( ${id},"${tipo}")'>Download</button></td>`; // Círculo preenchido se existir
          } else {
            circulos += "<td>⚪</td> "; // Círculo vazio se não existir
          }
        });
        lista += "<tr class='row'>" +
             "<td>" + dado.id + "</td>" +
             circulos +
             // botão vermelho (danger)
             
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
  async function download(id,template) {
    console.log("Baixando PDF para o orçamento com ID:", id);
    
  
    fetch(`/download/${id}/${template}`, {
      method: "GET",
    })
      .then(response => {
        if (!response.ok) {
          throw new Error("Erro ao gerar PDF.");
        }
        return response.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "orcamento.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();
      })
      .catch(error => {
        console.error("Erro:", error);
        alert("Não foi possível gerar o PDF.");
      })
      .finally(() => {
        btn.innerHTML = "Baixar PDF";
        btn.disabled = false;
      });
  }
  window.onload = function() {
    atualizaOrcamento();
  }
