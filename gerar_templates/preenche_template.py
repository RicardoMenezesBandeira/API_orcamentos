#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from decimal import Decimal

def parse_price(price_str):
    """
    Converte strings do tipo "R$ 1.234,56" em Decimal(1234.56).
    Caso não seja possível converter, retorna Decimal(0).
    """
    if not price_str:
        return Decimal("0")
    # Remove "R$", espaços e substitui vírgula por ponto
    normalized = price_str.upper().replace("R$", "").strip().replace(".", "").replace(",", ".")
    # Tenta converter em decimal
    try:
        return Decimal(normalized)
    except:
        return Decimal("0")

def format_price(value):
    """
    Converte um Decimal ou float em uma string no formato "R$ X.XXX,YY".
    Ex.: Decimal('1234.56') -> "R$ 1.234,56".
    """
    # Transformamos em string com duas casas decimais, usando ',' como separador decimal
    # e '.' como separador de milhar.
    int_part, frac_part = divmod(value, 1)
    int_part_str = f"{int(int_part):,}".replace(",", ".")  # Usa '.' para milhares
    cents = f"{int(round(frac_part * 100)):02d}"
    return f"R$ {int_part_str},{cents}"

def replace_all_placeholders(text, data_dict):
    """
    Substitui todos os placeholders {{alguma_coisa}} presentes em 'text' 
    pelos valores encontrados em data_dict. 
    - Se 'alguma_coisa' não existir em data_dict, substitui por string vazia.
    - Captura também casos com espaços, ex. {{  item_descricao }}.
    """

    # Padrão para capturar qualquer coisa entre {{ e }}
    pattern = re.compile(r"{{\s*([^}]*)\s*}}")
    
    def replacer(match):
        # O nome do placeholder é o grupo 1
        placeholder_name = match.group(1)
        # Se existir no dicionário, retorna o valor
        # Caso contrário, retorna vazio
        return data_dict.get(placeholder_name, "")
    
    return pattern.sub(replacer, text)

import re

def insert_br_after_underscores(html):
    """
    Procura no HTML por sequências de 5 ou mais underscores e insere um <br>
    logo após elas, se ainda não houver um <br>.
    """
    # O padrão procura por uma sequência de 5 ou mais underscores
    # (não permite que já haja um <br> logo após)
    pattern = re.compile(r'(_{5,})(?!<br>)')
    # Insere um <br> após a sequência encontrada
    return pattern.sub(r'\1<br><br>', html)

# ----------------------------------------------------------
#                INÍCIO DO SCRIPT PRINCIPAL
# ----------------------------------------------------------

# Nome dos arquivos
input_filename = "proposta_Petroleo_Brasileiro_convertida.htm"
output_filename = "proposta_Petroleo_Brasileiro_preenchida.htm"

# 1) Lê o conteúdo do template
with open(input_filename, "r", encoding="windows-1252") as f:
    html_content = f.read()

# 2) Preparação dos dados de exemplo
items_data = [
    {
        "item_descricao": "Produto A",
        "item_codigo": "A001",
        "item_quantidade": "10",
        "item_preco_unitario": "R$ 50,00",
        "item_preco_total": "R$ 500,00"
    },
    {
        "item_descricao": "Serviço B",
        "item_codigo": "S002",
        "item_quantidade": "2",
        "item_preco_unitario": "R$ 300,00",
        "item_preco_total": "R$ 600,00"
    },
    {
        "item_descricao": "Produto C",
        "item_codigo": "C003",
        "item_quantidade": "5",
        "item_preco_unitario": "R$ 100,00",
        "item_preco_total": "R$ 500,00"
    }
]

# Adicionamos o campo "numero" a cada item, e calculamos a soma dos "item_preco_total"
total_geral = Decimal("0")
for idx, item in enumerate(items_data):
    # 2.1) Define o numero (começando em 1)
    item["numero"] = str(idx+1)
    
    # 2.2) Faz o parse do item_preco_total para somar
    valor = parse_price(item.get("item_preco_total", "0"))
    total_geral += valor

# Formata a soma total de todos os itens (caso seja usado em global_data)
preco_total_itens_calculado = format_price(total_geral)

# 3) Processamento da tabela de itens, localizando onde há {{item_descricao}}
table_pattern = re.compile(r"(<table[^>]*>)(.*?{{\s*item_descricao\s*}}.*?)(</table>)",
                           re.DOTALL | re.IGNORECASE)
table_match = table_pattern.search(html_content)

if table_match:
    table_open = table_match.group(1)  # <table ...>
    table_body = table_match.group(2)  # conteúdo interno
    table_close = table_match.group(3) # </table>

    # Separa o body em linhas, usando </tr> (com possíveis espaços e ignorecase)
    parts = re.split(r"(</tr\s*>)", table_body, flags=re.IGNORECASE)
    
    header_parts = ""
    product_row_template = None
    footer_parts = ""

    i = 0
    while i < len(parts):
        current_chunk = parts[i]
        # Se o chunk contiver {{item_descricao}}, pegamos essa linha + seu </tr>
        if re.search(r"{{\s*item_descricao\s*}}", current_chunk):
            # Garante que, se existir o delimitador </tr>, seja concatenado
            if i+1 < len(parts):
                product_row_template = current_chunk + parts[i+1]
            else:
                product_row_template = current_chunk
            i += 2
            break
        else:
            # Esse pedaço ainda é cabeçalho
            if i+1 < len(parts):
                header_parts += current_chunk + parts[i+1]
            else:
                header_parts += current_chunk
            i += 2
    
    footer_parts = "".join(parts[i:])  # resto é footer
    
    if product_row_template is None:
        print("Não encontramos a linha de item contendo {{item_descricao}}.")
    else:
        # 3.1) Gera as linhas clonadas para cada item
        generated_rows = ""
        for item in items_data:
            # Substitui placeholders do item (inclusive se tiver "numero", etc.)
            row = replace_all_placeholders(product_row_template, item)
            generated_rows += row
        
        # Reconstrói a tabela
        new_table_body = header_parts + generated_rows + footer_parts
        new_table = table_open + new_table_body + table_close
        
        # Substitui no html
        start, end = table_match.span()
        html_content = html_content[:start] + new_table + html_content[end:]
else:
    print("Tabela contendo '{{item_descricao}}' não encontrada no HTML.")

# 4) Substituição dos dados globais
global_data = {
    "data": "01/04/2025",
    "numero_proposta": "12345",
    "cliente_nome": "Empresa Exemplo Ltda.",
    "cliente_cnpj": "12.345.678/0001-90",
    "ie": "123.456.789.012",
    "cliente_endereco": "Rua Exemplo, 123, Bairro, Cidade - UF",
    "cuidador": "João da Silva",
    "prazo_entrega": "10 dias úteis",
    "n_itens": str(len(items_data)),
    "soma_qtdes": str(sum(int(x.get("item_quantidade","0")) for x in items_data)),
    "total_outros": "R$ 0,00",
    # Usamos o valor calculado para preco_total_itens
    "preco_total_itens": preco_total_itens_calculado,
    "preco_frete": "R$ 100,00",
    "total_proposta": "R$ 1.700,00",
    "vendedor": "Johny D.",
    "validade": "30 Dias"
}

# Aplica a substituição usando a mesma função de placeholders
html_content = replace_all_placeholders(html_content, global_data)

html_content = insert_br_after_underscores(html_content)

# 5) Salva o HTML final
with open(output_filename, "w", encoding="windows-1252") as f:
    f.write(html_content)

print(f"Arquivo gerado com sucesso: {output_filename}")
