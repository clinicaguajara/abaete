def format_date(iso_date):
    """
    Converte uma data ISO 8601 (YYYY-MM-DDTHH:MM:SS.ssssss) em dia, mês e ano.
    
    Args:
        iso_date (str): Data no formato ISO 8601.

    Returns:
        tuple: (dia, mês, ano) como inteiros.
    """
    if not iso_date:
        return None, None, None  # Retorna valores vazios se a data for inválida

    try:
        date_obj = datetime.strptime(iso_date.split("T")[0], "%Y-%m-%d")  # Pega só a parte da data
        return date_obj.day, date_obj.month, date_obj.year
    except ValueError:
        return None, None, None  # Retorna valores vazios se o formato estiver errado