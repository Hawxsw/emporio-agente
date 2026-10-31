"""Extracts the store policy manual (PDF) and splits the text by section."""
import re
from functools import lru_cache

from pypdf import PdfReader

from src.config import DATA_DIR

SECTIONS = {
    "about": "1. Sobre a Empório da Música",
    "hours": "2. Horário de Funcionamento",
    "payment": "3. Formas de Pagamento",
    "returns": "4. Política de Trocas e Devoluções",
    "shipping": "5. Política de Frete e Entregas",
    "promotions": "6. Promoções e Descontos",
    "customer_service": "7. Atendimento via WhatsApp",
    "warranty": "8. Garantia",
    "privacy": "9. Privacidade e Proteção de Dados",
    "final_provisions": "10. Disposições Finais",
}


@lru_cache(maxsize=1)
def load_sections() -> dict[str, str]:
    reader = PdfReader(DATA_DIR / "políticas_da_loja.pdf")
    text = " ".join(page.extract_text() for page in reader.pages)
    text = " ".join(text.split())
    text = re.sub(r"Página \d+", " ", text)
    text = text.replace("Empório da Música Manual de Políticas e Procedimentos", " ")

    titles = list(SECTIONS.items())
    sections = {}
    for i, (topic, title) in enumerate(titles):
        start = text.index(title)
        end = text.index(titles[i + 1][1]) if i + 1 < len(titles) else len(text)
        sections[topic] = " ".join(text[start:end].split())
    return sections
