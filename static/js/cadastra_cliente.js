
window.onload = function() {

}
function Cadastra_cliente() {
    const inputs = document.querySelectorAll('.form-grid input');
    data={}
    inputs.forEach(input => {
        if (input.value == "") {
            alert("Preencha todos os campos");
            return;
        }
        data[input.name]= input.value
    });
    console.log(data)
    fetch('/cadastra_cliente', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(data)
    })

}

function voltar() {
    window.location.href = "/dashboard";
}