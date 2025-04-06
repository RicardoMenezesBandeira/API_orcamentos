from jinja2 import Environment, FileSystemLoader
import json

# Simule seu JSON (ou carregue de um arquivo)
dados= {
  "nome": "123",
  "endereco": "asd",
  "bairro": "asd",
  "data": "123123-03-12",
  "prazo": "1231-03-12",
  "resposanvel": "asd",
  "canalVenda": "asd@asd",
  "CentroCusto": "asdasd",
  "celular": "123",
  "Prazo??": "asd",
  "NdOrçamento": "123",
  "Produto": "123",
  "detalhesP": "asd",
  "qtdP": "123",
  "ValorP": "123",
  "serviço": "sad",
  "detalhesS": "asd",
  "qtdS": "123",
  "ValorS": "123",
  "NomeFrete": "asd",
  "Transportadora": "asd",
  "ref_endereco": "asd",
  "ProdutosT": "asd",
  "ServiçosT": "asd",
  "DescontoTFlat": "123",
  "DescontoTPercent": "123",
  "Avista": "123",
  "Parcelado": "123",
  "FormaPagamento": "123"
}

def renderizar_template(dados,template):
    # Configure o ambiente Jinja2
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template)  # seu arquivo HTML

    # Renderize o template com os dados
    html_renderizado = template.render(dados)
    return html_renderizado
# Salve em um novo arquivo HTML (opcional)
html = renderizar_template(dados,'template/pc_asallas.html')
with open('proposta_renderizada.html', 'w', encoding='utf-8') as f:
    f.write(html)
