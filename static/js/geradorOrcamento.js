// gera contador inicial (se você precisar reutilizar ele em correção, ok)
let produtoCount = 1;

// Adiciona novo produto
document.getElementById('add-produto').addEventListener('click', () => {
  produtoCount++;
  const container = document.getElementById('produtos-container');
  const novo = document.createElement('div');
  novo.className = 'produto form-group-set';
  novo.innerHTML = `
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
  container.appendChild(novo);
});

// Transforma FormData em objeto e depois em JSON
function formDataToJson(formData) {
  const data = {};

  // 1) coleta *todos* os templates marcados
  //    observe que mudamos o name para "templates[]"
  data.templates = formData.getAll('templates[]');

  // 2) coleta produtos
  const produtos = [];
  const nums = formData.getAll('numero[]');
  const nomes = formData.getAll('produto[]');
  const qtds = formData.getAll('qtd[]');
  const uns = formData.getAll('un[]');
  const vus = formData.getAll('valor_unitario[]');
  const tls = formData.getAll('total_local[]');
  for (let i = 0; i < nums.length; i++) {
    produtos.push({
      numero: nums[i],
      produto: nomes[i],
      quantidade: qtds[i],
      unidade: uns[i],
      valor_unitario: vus[i],
      total_local: tls[i]
    });
  }
  data.produtos = produtos;

  // 3) copia demais campos (pulando arrays acima)
  formData.forEach((value, key) => {
    if (key === 'templates[]') return;
    if (key.endsWith('[]'))   return;
    data[key] = value;
  });

  return JSON.stringify(data, null, 2);
}

// Envia para /postTemplate
async function enviarOrcamento(jsonData) {
  try {
    const resp = await fetch("http://127.0.0.1:8000/postTemplate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jsonData
    });
    if (resp.ok) {
      window.location.href = "/verification";
    } else {
      const err = await resp.json();
      alert("Erro: " + (err.erro || "desconhecido"));
    }
  } catch (e) {
    console.error(e);
    alert("Falha ao enviar dados");
  }
}

// Listener do form principal
document.querySelector('.form-grid').addEventListener('submit', e => {
  e.preventDefault();
  const fm = new FormData(e.target);
  const jsonData = formDataToJson(fm);
  console.log("JSON enviado:", jsonData);
  enviarOrcamento(jsonData);
});

// função de voltar
function back() {
  window.location.href = "/dashboard";
}
