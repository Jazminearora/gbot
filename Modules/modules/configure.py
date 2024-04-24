import re
from Modules import cbot




button_pattern = re.compile(r"^🔧 (Configure search|Настроить поиск|Axtarışı tənzimlə) 🔧)$")


def get_button_pattern():
    return button_pattern