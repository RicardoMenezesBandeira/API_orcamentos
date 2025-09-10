import re
from babel.numbers import format_currency

def formatar_dinheiro_brl(valor: float, casas: int = 4, fmt: str = None) -> str:
    if fmt is None:
        fmt = "¤#,##0." + "0" * casas
    return format_currency(valor, "BRL", locale="pt_BR", format=fmt)

def formatar_cnpj(cnpj: str) -> str:       # :contentReference[oaicite:6]{index=6}
    cnpj = re.sub(r"\D", "", cnpj)
    return re.sub(r"^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$", r"\1.\2.\3/\4-\5", cnpj)

def formatar_cpf(cpf: str) -> str:         # :contentReference[oaicite:7]{index=7}
    cpf = re.sub(r"\D", "", cpf)
    return re.sub(r"^(\d{3})(\d{3})(\d{3})(\d{2})$", r"\1.\2.\3-\4", cpf)
