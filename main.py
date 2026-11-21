import json
from pathlib import Path

# Busca el catálogo en la misma carpeta que este programa.
ruta = Path(__file__).parent / "exercises.json"

# Lee los ejercicios sin modificar el archivo original.
with ruta.open(encoding="utf-8") as archivo:
    ejercicios = json.load(archivo)

print(f"Catálogo cargado: {len(ejercicios)} ejercicios.")

print("\nPrimeros 5 ejercicios:")
for ejercicio in ejercicios[:5]:
    print("-", ejercicio["name"])