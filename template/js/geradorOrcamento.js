
document.querySelector('.form-grid').addEventListener('submit', function (e) {
    e.preventDefault(); // evita envio padrão

    const formData = new FormData(e.target);
    const data = {};

    // Transforma os campos em chave: valor
    formData.forEach((value, key) => {
    data[key] = value;
    });

    // Agora você tem todas as variáveis organizadas no objeto `data`
    console.log("Dados do formulário:", data);

    // Exemplo: acessar valores individuais
    
    dataTratada = formDataToJson(formData);
    console.log("JSON:", formDataToJson(formData));
    enviarOrcamento(dataTratada);
    // Adicione outros campos conforme necessidade


});

function formDataToJson(formData) {
    const jsonObject = {};

    formData.forEach((value, key) => {
        // Se a chave já existe, transforma em array para múltiplos valores (caso futuro)
        if (jsonObject.hasOwnProperty(key)) {
        if (!Array.isArray(jsonObject[key])) {
            jsonObject[key] = [jsonObject[key]];
        }
        jsonObject[key].push(value);
        } else {
        jsonObject[key] = value;
        }
    });

    return JSON.stringify(jsonObject, null, 2); // Retorna JSON formatado
}

async function enviarOrcamento(data) {
    try {
      const response = await fetch("http://127.0.0.1:8000/postTemplate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: data,
      });
      const result = await response.json();
      console.log("Resposta da API:", result);
    } catch (error) {
      console.error("Erro ao enviar:", error.message);
    }
  }


  let produtoCount = 1;
  let servicoCount = 1;

  function criarBotaoRemover(parentElement) {
    const btn = document.createElement("button");
    btn.innerHTML = "×";
    btn.className = "remove-btn";
    btn.type = "button";
    btn.onclick = () => {
      if (parentElement.classList.contains("produto")) {
        produtoCount--;
      } else if (parentElement.classList.contains("servico")) {
        servicoCount--;
      }
      parentElement.remove();
    };
    parentElement.appendChild(btn);
  }

  
  document.getElementById("add-produto").addEventListener("click", () => {
    produtoCount++;
    const container = document.getElementById("produtos-container");
    const novoProduto = document.createElement("div");
    novoProduto.classList.add("produto", "form-group-set");
    novoProduto.innerHTML = `
    <div class="flex-row">
      <div class="form-group"><label>Produto ${produtoCount}:</label><input type="text" name="Produto_${produtoCount}"></div>
      <div class="form-group"><label>Detalhes:</label><input type="text" name="detalhesP_${produtoCount}"></div>
    </div>
    <div class="flex-row">
      <div class="form-group"><label>Quantidade:</label><input type="number" name="qtdP_${produtoCount}"></div>
      <div class="form-group"><label>Valor:</label><input type="number" name="ValorP_${produtoCount}"></div>
    </div>
  `;
    criarBotaoRemover(novoProduto);
    container.appendChild(novoProduto);
  });
  
  document.getElementById("add-servico").addEventListener("click", () => {
    servicoCount++;
    const container = document.getElementById("servicos-container");
    const novoServico = document.createElement("div");
    novoServico.classList.add("servico", "form-group-set");
    novoServico.innerHTML = `
    <div class="flex-row">
      <div class="form-group"><label>Serviço ${servicoCount}:</label><input type="text" name="servico_${servicoCount}"></div>
      <div class="form-group"><label>Detalhes:</label><input type="text" name="detalhesS_${servicoCount}"></div>
    </div>
    <div class="flex-row">
      <div class="form-group"><label>Quantidade:</label><input type="number" name="qtdS_${servicoCount}"></div>
      <div class="form-group"><label>Valor:</label><input type="number" name="ValorS_${servicoCount}"></div>
    </div>
  `;
    criarBotaoRemover(novoServico);
    container.appendChild(novoServico);
  });