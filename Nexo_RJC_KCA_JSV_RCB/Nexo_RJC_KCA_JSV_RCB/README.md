# Nexo_RJC_KCA_JSV_RCB

Entrega tecnica del reto `Operacion Nexo 5G/6G` para Nueva Pangea.

Incluye:

- `index.html`: pagina web estatica lista para abrir en local o publicar en GitHub.
- `assets/figures/`: figuras generadas a partir de los calculos.
- `files/`: anexos en HTML, Markdown y CSV.
- `src/nexo/`: codigo Python reproducible.

## Abrir la pagina

1. Abre `index.html`.
2. Si quieres, usa `ABRIR_EN_GOOGLE_CHROME.bat`.

## Recalcular resultados

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
set PYTHONPATH=src
python -m nexo.main
```
