// Contador de produtos inicial
let produtoCount = 1;
let clientes = [];
let url = window.location.origin;
// Função para formatar valores em dinheiro no padrão brasileiro
const inputNumero = document.getElementById('numero');
window.onload = function() {
  fetch(url+'/get_cliente')
    .then(response => response.json())
    .then(data => {
    clientes = data;
  console.log(clientes);})
    .catch(error => {
      console.error('Erro ao buscar clientes:', error);
    });

}


  
   //Formata um número de telefone para o formato: +dd (xx) 12345-6789
   
  function formataUmaStringDeDigitosParaTelefone(digitos) {
  digitos = digitos || '';
  const total = digitos.length;
  let resultado = '';

  if (total > 11) {
    // Formato internacional: +cc (xx) xxxxx-xxxx
    const codigoPais = digitos.slice(0, 2);
    const ddd = digitos.slice(2, 4);
    const parte1 = digitos.slice(4, 9);
    const parte2 = digitos.slice(9, 13);

    resultado = `+${codigoPais} (${ddd}) ${parte1}`;
    if (parte2) {
      resultado += `-${parte2}`;
    }

  } else if (total === 11) {
    // Nacional com 9 dígitos (celular): (xx) x xxxx-xxxx
    const ddd = digitos.slice(0, 2);
    const parte1 = digitos.slice(2, 3);
    const parte2 = digitos.slice(3, 7);
    const parte3 = digitos.slice(7, 11);

    resultado = `(${ddd}) ${parte1} ${parte2}`;
    if (parte3) {
      resultado += `-${parte3}`;
    }

  } else {
    // Nacional com 8 dígitos (fixo): (xx) xxxx-xxxx
    const ddd = digitos.slice(0, 2);
    const parte1 = digitos.slice(2, 6);
    const parte2 = digitos.slice(6, 10);

    resultado = `(${ddd}) ${parte1}`;
    if (parte2) {
      resultado += `-${parte2}`;
    }
  }

  return resultado;
}


    /**
     * 2) Na hora do input:
     *    - Capturamos o cursor (selectionStart).
     *    - Contamos quantos dígitos existem ANTES desse cursor.
     *    - Extraímos todos os dígitos da string.
     *    - Reformatamos apenas pela “string limpa de dígitos”.
     *    - Calculamos a nova posição do cursor para ficar justo depois do mesmo dígito.
     */
    document.addEventListener('DOMContentLoaded', () => {
      const inp = document.getElementById('telefone');

      inp.addEventListener('input', (e) => {
        // 1) Captura o cursor antes de qualquer modificação
        const valorAtual     = e.target.value;           // string possívelmente formatada / com dígitos e parênteses etc.
        const posCursorAntes = e.target.selectionStart;  // posição do cursor no valor atual

        // 2) Descobrimos “quantos dígitos” existem antes desse cursor:
        let contagemDigitosAteCursor = 0;
        for (let i = 0; i < posCursorAntes; i++) {
          if (/\d/.test(valorAtual[i])) {
            contagemDigitosAteCursor++;
          }
        }

        // 3) Extraímos somente os dígitos (remove tudo que não for [0-9])
        const soDigitos = valorAtual.replace(/\D/g, '');

        // 4) Reformatamos todos os dígitos (mesma lógica anterior, mas agora só recebe string de dígitos)
        const textoFormatado = formataUmaStringDeDigitosParaTelefone(soDigitos);

        // 5) Calculamos onde o cursor deve ficar de acordo com “contagemDigitosAteCursor”
        //    Ou seja: andamos no textoFormatado contando dígitos até chegar a “contagemDigitosAteCursor”,
        //    então posicionamos o cursor logo após este dígito.
        let novaPosCursor = 0;
        let digitosContados = 0;
        while (novaPosCursor < textoFormatado.length && digitosContados < contagemDigitosAteCursor) {
          if (/\d/.test(textoFormatado[novaPosCursor])) {
            digitosContados++;
          }
          novaPosCursor++;
        }

        // 6) Reatribui o valor e reposiciona o cursor
        e.target.value = textoFormatado;
        e.target.setSelectionRange(novaPosCursor, novaPosCursor);
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
        <div class="form-group"><label>Produto:</label><textarea name="produto[]" required rows="1" oninput="autoGrow(this)"></textarea></div>
      </div>
    </div>
    <div class="flex-row">
      <div class="form-group">
        <label>Quantidade:</label>
        <input type="text" name="qtd[]" step="0.0001" min="0" onkeydown="return blockDotComma(event)">
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
    const response = await fetch(url+"/postTemplate", {
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
function parseValorBrasileiro(valor) {
  if (!valor) return 0;
  return parseFloat(
    valor.replace(/\./g, '').replace(',', '.')
  ) || 0;
}
// função que recalcula totais
function recalcularResumo() {
  const linhas = produtosContainer.querySelectorAll('.produto');
  let somaQtd = 0;
  let somaValor = 0;

  linhas.forEach(linha => {
    const qtdInput   = linha.querySelector('input[name="qtd[]"]');
    const unitInput  = linha.querySelector('input[name="valor_unitario[]"]');
    const totalInput = linha.querySelector('input[name="total_local[]"]');
    

    const qtd  = parseValorBrasileiro(qtdInput.value)   || 0;
    const unit = parseValorBrasileiro(unitInput.value)  || 0;
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


const cliente_campo = document.getElementById("cliente");
const cnpj_campo = document.getElementById("cnpj");
const sugestoes = document.getElementById("sugestoes");

cliente_campo.addEventListener("input", () => {
  buscarCliente(cliente_campo.value);
});
cnpj_campo.addEventListener("input", () => {
  buscarCliente(cnpj_campo.value);
});
function buscarCliente(inp){
    const query = inp.trim().toLowerCase();
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
}

function preencherFormulario(cliente) {
  const form = document.getElementById("form-grid");
  Object.entries(cliente).forEach(([key, value]) => {
    const input = form.querySelector(`[name="${key}"]`);
    if (input) input.value = value;
  });
}

  function autoGrow(element) {
  element.style.height = "auto";
  element.style.height = (element.scrollHeight) + "px";
}