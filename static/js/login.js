document.getElementById('loginForm').addEventListener('submit', async function(e) {
  e.preventDefault();

  const usuario = document.getElementById('usuario').value;
  const senha = document.getElementById('senha').value;
  let url =window.location.origin
  
  try {
      const response = await fetch(url+"/login", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
          },
          body: JSON.stringify({
              username: usuario,
              password: senha
          }),
          credentials: 'include' // Importante para cookies!
      });

      const data = await response.json(); // Adicionado para parsear a resposta

      if (!response.ok) {
          throw new Error(data.message || 'Erro no login');
      }

      // Armazena o token no localStorage (se necessário)
      if (data.token) {
          localStorage.setItem('ContrucomToken', data.token);
      }
      
      // Redireciona para a página principal

      window.location.href ="/dashboard";

  } catch (error) {
      console.error("Erro ao enviar:", error);
      alert(error.message || "Erro durante o login");
  }
});