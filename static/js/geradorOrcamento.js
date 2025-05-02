// Contador de produtos inicial
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

// Converte FormData em JSON, incluindo múltiplos templates
function formDataToJson(formData) {
  const data = {};

  // Coleta todos os templates marcados
  data.templates = formData.getAll('templates[]');

  // Monta array de produtos
  const produtos = [];
  const numeros = formData.getAll('numero[]');
  const nomes = formData.getAll('produto[]');
  const quantidades = formData.getAll('qtd[]');
  const unidades = formData.getAll('un[]');
  const valoresUnitarios = formData.getAll('valor_unitario[]');
  const totaisLocais = formData.getAll('total_local[]');
  for (let i = 0; i < numeros.length; i++) {
    produtos.push({
      numero: numeros[i],
      produto: nomes[i],
      quantidade: quantidades[i],
      unidade: unidades[i],
      valor_unitario: valoresUnitarios[i],
      total_local: totaisLocais[i]
    });
  }
  data.produtos = produtos;

  // Outros campos do formulário (não arrays)
  formData.forEach((value, key) => {
    if (key === 'templates[]' || key.endsWith('[]')) return;
    data[key] = value;
  });
  console.log("Dados do formulário:", data);
  return JSON.stringify(data, null, 2);
}

// Envia orçamento para a API
async function enviarOrcamento(data) {
  try {
    const response = await fetch("http://127.0.0.1:8000/postTemplate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: data
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

// Manipula o submit do formulário principal
document.querySelector('.form-grid').addEventListener('submit', function(e) {
  e.preventDefault();
  const formData = new FormData(this);
  const jsonData = formDataToJson(formData);
  console.log("Dados enviados:", jsonData);
  enviarOrcamento(jsonData);
});

// Função de voltar para o dashboard
function back() {
  window.location.href = "/dashboard";
}


// referência aos elementos
const produtosContainer = document.getElementById('produtos-container');
const totalItensInput    = document.getElementById('total-itens');
const valorTotalInput    = document.getElementById('valor-total');

// função que recalcula totais
function recalcularResumo() {
  const linhas = produtosContainer.querySelectorAll('.produto');
  let somaQtd = 0;
  let somaValor = 0;

  linhas.forEach(linha => {
    const qtdInput   = linha.querySelector('input[name="qtd[]"]');
    const unitInput  = linha.querySelector('input[name="valor_unitario[]"]');
    const totalInput = linha.querySelector('input[name="total_local[]"]');

    const qtd  = parseFloat(qtdInput.value)   || 0;
    const unit = parseFloat(unitInput.value)  || 0;
    const total = qtd * unit;

    // atualiza total da linha
    totalInput.value = total.toFixed(2);

    somaQtd   += qtd;
    somaValor += total;
  });

  // atualiza resumo
  totalItensInput.value = somaQtd;
  valorTotalInput.value = somaValor.toFixed(2);
}

// dispara recálculo toda vez que mudar qtd ou valor unitário
produtosContainer.addEventListener('input', (e) => {
  if (e.target.matches('input[name="qtd[]"], input[name="valor_unitario[]"]')) {
    recalcularResumo();
  }
});

// também recalcule quando adicionar ou remover produtos
document.getElementById('add-produto').addEventListener('click', () => {
  // seu código existente que cria a nova linha...
  // depois de adicionar:
  recalcularResumo();
});

// quando remove um produto
produtosContainer.addEventListener('click', e => {
  if (e.target.matches('.remove-btn')) {
    // espera a remoção do DOM, depois:
    setTimeout(recalcularResumo, 0);
  }
});

// recálculo inicial (caso tenha itens pré-existentes)
document.addEventListener('DOMContentLoaded', recalcularResumo);