import re

def formatar_dinheiro_brl(valor, casas: int = 4) -> str:
    """
    Formata número no padrão brasileiro:
    - Ponto para milhar
    - Vírgula para decimais
    - 'casas' casas decimais fixas (default=4)
    """

    print(f"[DEBUG] formatar_dinheiro_brl chamado com valor={valor}, casas={casas}")
    # Se for string, normaliza para float
    if isinstance(valor, str):
        valor = valor.strip()
        if "," in valor and "." in valor:
            valor = valor.replace(".", "").replace(",", ".")
        elif "," in valor:
            valor = valor.replace(",", ".")
        valor = float(valor)

    # Força arredondamento e casas fixas
    inteiro, decimal = divmod(abs(valor), 1)
    decimal_str = f"{decimal:.{casas}f}"[2:]  # pega só os dígitos após o ponto

    # Parte inteira com separador de milhar
    inteiro_str = f"{int(inteiro):,}".replace(",", ".")

    # Junta com vírgula
    resultado = f"{'-' if valor < 0 else ''}{inteiro_str},{decimal_str}"

    print(f"[DEBUG] formatar_dinheiro_brl resultado: {resultado}")

    return resultado



def formatar_cnpj(cnpj: str) -> str:       # :contentReference[oaicite:6]{index=6}
    cnpj = re.sub(r"\D", "", cnpj)
    return re.sub(r"^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$", r"\1.\2.\3/\4-\5", cnpj)

def formatar_cpf(cpf: str) -> str:         # :contentReference[oaicite:7]{index=7}
    cpf = re.sub(r"\D", "", cpf)
    return re.sub(r"^(\d{3})(\d{3})(\d{3})(\d{2})$", r"\1.\2.\3-\4", cpf)
