
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
      if (key === "templates") {
          // Sempre transforma em array, mesmo que tenha só um elemento
          if (!jsonObject[key]) {
              jsonObject[key] = [];
          }
          jsonObject[key].push(value);
      } else {
          // Se a chave já existe, transforma em array (casos raros, fora 'templates')
          if (jsonObject.hasOwnProperty(key)) {
              if (!Array.isArray(jsonObject[key])) {
                  jsonObject[key] = [jsonObject[key]];
              }
              jsonObject[key].push(value);
          } else {
              jsonObject[key] = value;
          }
      }
  });

  return JSON.stringify(jsonObject, null, 2);
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

    if (response.ok) {
      // Redireciona manualmente para a página de verificação
      window.location.href = "http://127.0.0.1:8000/verification";
    } else {
      const result = await response.json();
      console.error("Erro na resposta da API:", result);
    }
  } catch (error) {
    console.error("Erro ao enviar:", error.message);
  }
}
