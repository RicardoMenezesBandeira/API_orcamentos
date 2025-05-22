// Contador de produtos inicial
let produtoCount = 1;
let clientes = [];
// Função para formatar valores em dinheiro no padrão brasileiro
const inputNumero = document.getElementById('numero');
window.onload = function() {
  fetch('/get_cliente')
    .then(response => response.json())
    .then(data => {
    clientes = data;
  console.log(clientes);})
    .catch(error => {
      console.error('Erro ao buscar clientes:', error);
    });

}


  
   //Formata um número de telefone para o formato: +dd (xx) 12345-6789
   
  function formatTelefone(valor) {
    // Remove tudo que não seja dígito
    const apenasDigitos = (valor || '').replace(/\D/g, '');

    // Extrai cada parte:
    const codigoPais = apenasDigitos.slice(0, 2);   // primeiros 2 dígitos
    const ddd        = apenasDigitos.slice(2, 4);   // dígitos 3 e 4
    const resto      = apenasDigitos.slice(4);      // a partir do 5º dígito

    let numeroFormatado = '';

    // Se houver código de país, começa com "+"
    if (codigoPais) {
      numeroFormatado += '+' + codigoPais;
    }

    // Se houver DDD, coloca entre parênteses
    if (ddd) {
      numeroFormatado += ' (' + ddd + ')';
    }

    // Formata os dígitos restantes como "12345-6789"
    if (resto) {
      // Se tiver mais de 5 dígitos, insere hífen após os primeiros 5
      if (resto.length > 5) {
        const parte1 = resto.slice(0, 5);
        const parte2 = resto.slice(5, 9); // até 4 dígitos após os 5 primeiros
        numeroFormatado += ' ' + parte1 + (parte2 ? ('-' + parte2) : '');
      } else {
        // Se tiver 5 ou menos, mostra só sem hífen
        numeroFormatado += ' ' + resto;
      }
    }

    return numeroFormatado.trim();
  }

  // Quando o DOM terminar de carregar, anexamos o listener ao input
  document.addEventListener('DOMContentLoaded', () => {
    const inputTelefone = document.getElementById('telefone');

    inputTelefone.addEventListener('input', (e) => {
      // A cada digitação, substitui o valor pelo formatado
      e.target.value = formatTelefone(e.target.value);
    });
  });


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
    const response = await fetch("/postTemplate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: data
    });
    const result = await response.json();
    if (response.ok) {
      // agora temos result.id
      const id = result.id;
      // manda já o primeiro template (idx=0)
      window.location.href = `/verification?json_file=${id}.json&template_idx=0`;
    } else {
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
// avança para o cadastro de cliente
function cadastra_cliente() {
  window.location.href = "/p_cadastro_cliente";
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


const buscaInput = document.getElementById("busca-nome");
const sugestoes = document.getElementById("sugestoes");

buscaInput.addEventListener("input", () => {
    const query = buscaInput.value.trim().toLowerCase();
    if (query.length < 2) {
        sugestoes.innerHTML = "";
        sugestoes.style.display = "none";
        return;
    }

     const encontrados = clientes.filter(c =>
    (c.cliente && c.cliente.toLowerCase().includes(query)) ||
    (c.cnpj && c.cnpj.toLowerCase().includes(query))
  );

    sugestoes.innerHTML = "";
    encontrados.forEach(cliente => {
        const li = document.createElement("li");
        li.textContent = cliente.cliente+" - " + cliente.cnpj;
        li.style.cursor = "pointer";
        li.onclick = () => {
            preencherFormulario(cliente);
            sugestoes.innerHTML = "";
            sugestoes.style.display = "none";
        };
        sugestoes.appendChild(li);
    });

    sugestoes.style.display = encontrados.length ? "block" : "none";
});
function preencherFormulario(cliente) {
  const form = document.getElementById("form-grid");
  Object.entries(cliente).forEach(([key, value]) => {
    const input = form.querySelector(`[name="${key}"]`);
    if (input) input.value = value;
  });
}