  
  function novoOrcamento(){
    // Redireciona para a página principal
    window.location.href = "/preencher";
  }
  function novoFuncionario(){
    // Redireciona para a página principal
    window.location.href = "/cadastro";
  }
  function atualizaOrcamento(){
    fetch('/orçaemnto', {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/json',
        // Inclua o token de autenticação se necessário
        // 'Authorization': 'Bearer SEU_TOKEN_AQUI'
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Erro na requisição: ' + response.status);
      }
      return response.json();
    })
    .then(data => {
      console.log('Dados recebidos:', data);
      // Aqui você pode manipular os dados recebidos, como atualizar o DOM
    })
    .catch(error => {
      console.error('Erro ao buscar os dados:', error);
    });
    }
  
  window.onload = function() {
    atualizaOrcamento();
  }
