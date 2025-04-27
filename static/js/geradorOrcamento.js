// Contador de produtos
let produtoCount = 1;

// Função para adicionar novo produto
document.getElementById('add-produto').addEventListener('click', () => {
  produtoCount++;
  const container = document.getElementById('produtos-container');
  
  const novoProduto = document.createElement('div');
  novoProduto.className = 'produto form-group-set';
  novoProduto.innerHTML = `
    <div class="flex-row">
      <div class="form-group">
        <label>Número do item:</label>
        <input type="number" name="numero[]" value="${produtoCount}" readonly>
      </div>
      <div class="form-group">
        <label>Produto:</label>
        <input type="text" name="produto[]">
      </div>
    </div>
    <div class="flex-row">
      <div class="form-group">
        <label>Quantidade:</label>
        <input type="number" name="qtd[]">
      </div>
      <div class="form-group">
        <label>Unidade:</label>
        <input type="text" name="un[]">
      </div>
    </div>
    <div class="flex-row">
      <div class="form-group">
        <label>Valor Unitário (R$):</label>
        <input type="number" step="0.01" name="valor_unitario[]">
      </div>
      <div class="form-group">
        <label>Valor Total (R$):</label>
        <input type="number" step="0.01" name="total_local[]">
      </div>
    </div>
    <button type="button" class="remove-btn" onclick="this.parentNode.remove()">×</button>
  `;
  
  container.appendChild(novoProduto);
});

// Função para converter FormData em JSON com produtos como array
function formDataToJson(formData) {
  const data = {};
  const produtos = [];
  
  // Coletar todos os arrays de campos
  const numeros = formData.getAll('numero[]');
  const produtosNomes = formData.getAll('produto[]');
  const quantidades = formData.getAll('qtd[]');
  const unidades = formData.getAll('un[]');
  const valoresUnitarios = formData.getAll('valor_unitario[]');
  const totaisLocais = formData.getAll('total_local[]');
  
  // Construir array de produtos
  for (let i = 0; i < numeros.length; i++) {
    produtos.push({
      numero: numeros[i],
      produto: produtosNomes[i],
      quantidade: quantidades[i],
      unidade: unidades[i],
      valor_unitario: valoresUnitarios[i],
      total_local: totaisLocais[i]
    });
  }
  
  // Adicionar outros campos ao objeto principal
  formData.forEach((value, key) => {
    if (!key.endsWith('[]')) {
      data[key] = value;
    }
  });
  
  // Adicionar array de produtos
  data.produtos = produtos;
  
  return JSON.stringify(data, null, 2);
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
      const result = await response.json();
      alert("Erro: " + (result.erro || "Erro desconhecido"));
    }
  } catch (error) {
    console.error("Erro ao enviar:", error);
    alert("Erro ao enviar os dados");
  }
}

// Event listener para o formulário
document.querySelector('.form-grid').addEventListener('submit', function(e) {
  e.preventDefault();
  const formData = new FormData(this);
  const jsonData = formDataToJson(formData);
  console.log("Dados enviados:", jsonData);
  enviarOrcamento(jsonData);
});

function back() {
  window.location.href = "/dashboard";
}