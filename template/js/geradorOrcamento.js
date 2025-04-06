const axios = require('axios');

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
    const numero = data.nome;
    const cliente = data.endereco;
    const vendedor = data.bairro;
    const dataOrcamento = data.data;
    const prazoEntrega = data.prazo;
    const canalVenda = data.canalVenda;
    const produto = data.Produto;
    const qtdProduto = data.qtdP;
    const valorProduto = data.ValorP;

    console.log("Número:", numero);
    console.log("Cliente:", cliente);
    console.log("Produto:", produto);
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
    const response = await axios.post("http://127.0.0.1:8000/postTemplate", data);
    console.log("Resposta da API:", response.data);
    } catch (error) {
    console.error("Erro ao enviar:", error.response?.data || error.message);
    }
}