// Contadores iniciais
let produtoCount = 1;
let servicoCount = 1;

// Converte FormData em JSON
function formDataToJson(formData) {
  const jsonObject = {};
  formData.forEach((value, key) => {
    if (jsonObject.hasOwnProperty(key)) {
      if (!Array.isArray(jsonObject[key])) jsonObject[key] = [jsonObject[key]];
      jsonObject[key].push(value);
    } else {
      jsonObject[key] = value;
    }
  });
  return JSON.stringify(jsonObject, null, 2);
}

// Envia dados para a API
async function enviarOrcamento(data) {
  try {
    const response = await fetch("http://127.0.0.1:8000/postTemplate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: data,
    });
    if (response.ok) {
      window.location.href = "/verification";
    } else {
      return alert("Erro: " + result.erro);
    }
    const result = await response.json();
    console.log("Resposta da API:", result);
  } catch (error) {
    console.error("Erro ao enviar:", error.message);
  }
}

// Cria botão de remoção
function criarBotaoRemover(parentElement) {
  const btn = document.createElement("button");
  btn.innerHTML = "×";
  btn.className = "remove-btn";
  btn.type = "button";
  btn.onclick = () => {
    if (parentElement.classList.contains("produto")) produtoCount--;
    else if (parentElement.classList.contains("servico")) servicoCount--;
    parentElement.remove();
  };
  parentElement.appendChild(btn);
}

// Registra event listeners após o DOM carregar
document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('.form-grid');
  form?.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {};
    formData.forEach((value, key) => (data[key] = value));
    console.log("Dados do formulário:", data);
    const dataTratada = formDataToJson(formData);
    console.log("JSON:", dataTratada);
    enviarOrcamento(dataTratada);
  });

  const addP = document.getElementById("add-produto");

addP?.addEventListener("click", () => {
  produtoCount++;
  const container = document.getElementById("produtos-container");

  const novoProduto = document.createElement("div");
  novoProduto.classList.add("produto", "form-group-set");
  novoProduto.innerHTML = `
    <div class="flex-row">
      <div class="form-group">
        <label>Número do item:</label>
        <input type="number" name="numero_${produtoCount}" value="${produtoCount}" readonly>
      </div>
      <div class="form-group">
        <label>Produto:</label>
        <input type="text" name="produto_${produtoCount}">
      </div>
    </div>
    <div class="flex-row">
      <div class="form-group">
        <label>Quantidade:</label>
        <input type="number" name="qtd_${produtoCount}">
      </div>
      <div class="form-group">
        <label>Unidade:</label>
        <input type="text" name="un_${produtoCount}">
      </div>
    </div>
    <div class="flex-row">
      <div class="form-group">
        <label>Valor Unitário (R$):</label>
        <input type="number" step="0.01" name="valor_unitario_${produtoCount}">
      </div>
      <div class="form-group">
        <label>Valor Total (R$):</label>
        <input type="number" step="0.01" name="total_local_${produtoCount}">
      </div>
    </div>
  `;

  // Função que adiciona um botão de remover ao bloco (presumindo que você já a tenha definido)
  criarBotaoRemover(novoProduto);

  container.appendChild(novoProduto);
});

  const addS = document.getElementById("add-servico");
  addS?.addEventListener("click", () => {
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

  console.log('form-grid:', document.querySelector('.form-grid'));
  console.log('add-produto:', document.getElementById('add-produto'));
});