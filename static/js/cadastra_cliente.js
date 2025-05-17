window.onload = function() {
}
function Cadastra_cliente() {
}
function validarCampos() {
    var nome = document.getElementById("nome").value;
    var cpf = document.getElementById("cpf").value;
    var email = document.getElementById("email").value;
    var telefone = document.getElementById("telefone").value;

    if (nome == "" || cpf == "" || email == "" || telefone == "") {
        alert("Por favor, preencha todos os campos.");
        return false;
    }

    if (!validarCPF(cpf)) {
        alert("CPF inválido.");
        return false;
    }

    if (!validarEmail(email)) {
        alert("Email inválido.");
        return false;
    }

    return true;
}
function voltar() {
    window.location.href = "/dashboard";
}