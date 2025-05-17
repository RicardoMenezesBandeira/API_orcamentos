  let orcamento  = []
  function novoOrcamento(){
    // Redireciona para a página principal
    window.location.href = "/preencher";
  }
  function novoFuncionario(){
    // Redireciona para a página principal
    window.location.href = "/cadastro";
  }async function atualizaOrcamento() {
  try {
    const response = await fetch('/orçaemnto', {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error('Erro na requisição: ' + response.status);
    }

    const dados = await response.json();
    console.log('Dados recebidos:', dados);
    orcamento = dados;

    const orca = document.getElementById("orcamento");
    let lista = "<div class='content'>";

    dados.forEach(function(dado) {
        let templates = dado.templates || [];
        let id = dado.id;
        let circulos = '';
        const tipos = ['BossBR', 'PCasallas', 'Construcom'];

        tipos.forEach(tipo => {
          if (templates.includes(tipo)) {
            circulos += `<div><button class='btn btn-danger btn-sm' onclick='download(${id}, "${tipo}")'>${tipo}</button></div>`;
          } else {
            circulos += "<div>⚪</div>";
          }
        });

        const editButton = 
        `<div>
          <button class='btn btn-warning btn-sm'
                  onclick="
                    window.location.href=
                      '/verification?json_file=${dado.id}.json'
                  ">
            Editar
          </button>
        </div>`;


        lista += `<div class='row'>
          <div>${dado.numero}</div>
          <div>${dado.cliente}</div>
          <div>${dado.vendedor}</div>
          <div class='downloads'>${circulos}</div>
          <div class='editar'>${editButton}</div>
        </div>`;
      
    });

    lista += "</div>";
    orca.innerHTML = lista;

  } catch (error) {
    console.error('Erro ao buscar os dados:', error);
  }
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
function Logout() {
  const href = "/logout";
  fetch(href, {
    method: 'GET',
    credentials: 'include',
  })
  .then(async response => {
    const contentType = response.headers.get("content-type");  
      if (response.ok) {
        if (contentType && contentType.includes("application/json")) {
          // Caso venha JSON com mensagem de sucesso
          const data = await response.json();
          console.log(data.message||"mensagem vazia");
          window.location.href = "http://127.0.0.1:8000"; // Redireciona manualmente
        }
    } else {
      // Se for um erro (status HTTP 4xx ou 5xx)
      if (contentType && contentType.includes("application/json")) {
        const error = await response.json();
        alert("Erro: " + (error.message || "Erro desconhecido"));
      } else {
        alert("Erro ao fazer logout.");
      }
    }
  })
  .catch(err => {
    console.error("Erro na requisição:", err);
    alert("Erro na rede ou servidor.");
  });
  
}

function filtrarOrcamentos(valor) {
  const orca = document.getElementById("orcamento");
  let lista = "<div class='content'>";

  // Filtra a lista original com base no que foi digitado
  const resultados = orcamento.filter(dado => 
    dado.numero.toString().startsWith(valor)
  );

  resultados.forEach(function(dado) {
    let templates = dado.templates || [];
    let id = dado.id;
    let circulos = '';
    const tipos = ['BossBR', 'PCasallas', 'Construcom'];

    tipos.forEach(tipo => {
      if (templates.includes(tipo)) {
        circulos += `<div><button class='btn btn-danger btn-sm' onclick='download(${id}, "${tipo}")'>${tipo}</button></div>`;
      } else {
        circulos += "<div>⚪</div>";
      }
    });

    lista += "<div class='row'>" +
      "<div>" + dado.numero + "</div>" +
      "<div>" + dado.cliente + "</div>" +
      "<div>" + dado.vendedor + "</div>" +
      "<div class='downloads'>" + circulos + "</div>" +
      "</div>";
  });

  lista += "</div>";
  orca.innerHTML = lista;
}
