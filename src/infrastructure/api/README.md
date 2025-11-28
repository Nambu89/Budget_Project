# API REST - Calculadora de Presupuestos

## Descripción

API REST construida con FastAPI para exponer el motor de cálculo de presupuestos de reformas.

## Instalación

```bash
pip install fastapi uvicorn python-multipart
```

## Ejecución

### Desarrollo (con auto-reload)
```bash
python run_api.py
```

O directamente con uvicorn:
```bash
uvicorn src.infrastructure.api.main:app --reload --port 8000
```

### Producción
```bash
uvicorn src.infrastructure.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Documentación

Una vez iniciada la API, la documentación interactiva está disponible en:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Disponibles

### Health Check
- `GET /` - Información básica de la API
- `GET /health` - Health check

### Catálogos
- `GET /api/v1/catalogos/paquetes` - Lista de paquetes disponibles
- `GET /api/v1/catalogos/categorias` - Categorías de trabajo
- `GET /api/v1/catalogos/paises` - Países soportados

### Presupuestos
- `POST /api/v1/presupuesto/calcular` - Calcular presupuesto
- `POST /api/v1/presupuesto/pdf` - Generar PDF (pendiente)
- `POST /api/v1/presupuesto/explicar` - Explicación IA (pendiente)

## Ejemplo de Uso

### Calcular Presupuesto

```bash
curl -X POST "http://localhost:8000/api/v1/presupuesto/calcular" \
  -H "Content-Type: application/json" \
  -d '{
    "proyecto": {
      "tipo_inmueble": "piso",
      "metros_cuadrados": 80,
      "estado_actual": "a_reformar",
      "es_vivienda_habitual": true,
      "calidad_general": "estandar"
    },
    "trabajos": {
      "paquetes": [
        {"id": "bano_completo", "cantidad": 1, "metros": 5}
      ],
      "partidas": []
    },
    "modo": "particular",
    "pais": "ES"
  }'
```

### Obtener Paquetes

```bash
curl "http://localhost:8000/api/v1/catalogos/paquetes?pais=ES"
```

## Estructura

```
src/infrastructure/api/
├── main.py              # Aplicación FastAPI principal
├── routes/
│   ├── catalogos.py     # Endpoints de catálogos
│   └── presupuesto.py   # Endpoints de presupuestos
└── schemas/
    ├── request.py       # Modelos de request
    └── response.py      # Modelos de response
```

## CORS

La API está configurada para aceptar requests desde cualquier origen (`allow_origins=["*"]`).

**⚠️ En producción**, configurar dominios específicos:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio.com"],
    ...
)
```

## Próximos Pasos

- [ ] Implementar generación de PDF vía API
- [ ] Implementar explicación con IA
- [ ] Añadir autenticación para profesionales
- [ ] Rate limiting
- [ ] Caché de catálogos
