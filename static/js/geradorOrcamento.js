// Contador de produtos inicial
let produtoCount = 1;
// Função para formatar valores em dinheiro no padrão brasileiro
const inputNumero = document.getElementById('numero');

  // Ao sair do campo, já preenche os zeros
  inputNumero.addEventListener('blur', () => {
    let val = inputNumero.value;
    // Converte para string e adiciona zeros à esquerda até comprimento 4
    inputNumero.value = val.toString().padStart(4, '0');
  });
function formatarDinheiro(valorEmNumero) {
  return valorEmNumero.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 4,
    maximumFractionDigits: 4
  });
}

// Retorna a data de hoje no formato DD/MM/AAAA
function getDataHoje() {
  const hoje = new Date();
  const dia  = String(hoje.getDate()    ).padStart(2, '0');
  const mes  = String(hoje.getMonth() + 1).padStart(2, '0');
  const ano  = hoje.getFullYear();
  return `${dia}/${mes}/${ano}`;
}

document.addEventListener('DOMContentLoaded', () => {
  const inputData = document.getElementById('data');
  // Se estiver vazio, pré-preenche
  if (inputData && !inputData.value) {
    inputData.value = getDataHoje();
  }
  // Adiciona listener para forçar máscara enquanto digita (opcional)
  inputData.addEventListener('input', (e) => {
    let v = e.target.value.replace(/\D/g, '');
    if (v.length > 2) v = v.slice(0,2) + '/' + v.slice(2);
    if (v.length > 5) v = v.slice(0,5) + '/' + v.slice(5,9);
    e.target.value = v;
  });
});

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
        <input type="text" step="0.0001" name="valor_unitario[]">
      </div>
      <div class="form-group">
        <label>Valor Total (R$):</label>
        <input type="text" step="0.0001" name="total_local[]">
      </div>
    </div>
    <button type="button" class="remove-btn" onclick="this.parentNode.remove()">×</button>
  `;
  container.appendChild(novoProduto);
});

// Converte FormData em JSON, incluindo múltiplos templates
function formDataToJson(formData) {
  const data = {};// Coleta todos os templates marcados
    const checkboxes = document.querySelectorAll('input[name="templates[]"]');
    const algumMarcado = Array.from(checkboxes).some(cb => cb.checked);
    if (!algumMarcado) {
      alert("Selecione ao menos um template.");
      return false; // Impede o envio
    }
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
    totalInput.value = formatarDinheiro(total);

    somaQtd   += qtd;
    somaValor += total;
  });

  // atualiza resumo
  totalItensInput.value = somaQtd;
  valorTotalInput.value = formatarDinheiro(somaValor)
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