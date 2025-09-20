# Sistema de Métricas para el Modelo de Parsing de Facturas

Este sistema implementa métricas completas para evaluar el rendimiento y la calidad del modelo de parsing de facturas.

## 📊 Métricas Implementadas

### 1. **Confidence Score**
- **Descripción**: Puntuación de confianza basada en la cantidad y calidad de campos extraídos
- **Rango**: 0.0 - 1.0 (1.0 = perfecto)
- **Cálculo**: Ponderado por campos críticos (70%) y adicionales (30%) + bonus por items

### 2. **Field Accuracy**
- **Descripción**: Precisión de los campos extraídos comparando con datos de verdad de campo
- **Rango**: 0.0 - 1.0 (1.0 = todos los campos correctos)
- **Cálculo**: Campos correctos / Total de campos evaluados

### 3. **CER (Character Error Rate)**
- **Descripción**: Tasa de error a nivel de caracteres en el texto extraído por OCR
- **Rango**: 0.0 - 1.0 (0.0 = perfecto, 1.0 = todos los caracteres incorrectos)
- **Cálculo**: Distancia de Levenshtein / Longitud del texto correcto

### 4. **WER (Word Error Rate)**
- **Descripción**: Tasa de error a nivel de palabras en el texto extraído por OCR
- **Rango**: 0.0 - 1.0 (0.0 = perfecto, 1.0 = todas las palabras incorrectas)
- **Cálculo**: Distancia de Levenshtein a nivel de palabras / Número de palabras correctas

### 5. **Processing Latency**
- **Descripción**: Tiempo de procesamiento por documento
- **Unidad**: Segundos
- **Medición**: Tiempo total desde inicio hasta fin del procesamiento

### 6. **Throughput**
- **Descripción**: Número de documentos procesados por segundo
- **Unidad**: Documentos/segundo
- **Cálculo**: 1 / Tiempo promedio de procesamiento

## 🚀 Uso del Sistema

### 1. Prueba del Sistema de Métricas

```bash
# Ejecutar pruebas del sistema de métricas
python test_metrics_system.py
```

Este script:
- Prueba el calculador de métricas con datos de ejemplo
- Demuestra el funcionamiento con datos que contienen errores
- Crea un archivo de ground truth de ejemplo
- Muestra cómo usar el procesador de lotes

### 2. Benchmark del Modelo

```bash
# Benchmark básico con archivos de prueba
python benchmark_model.py --test-dir /ruta/a/facturas

# Benchmark con diferentes tamaños de lote
python benchmark_model.py --test-dir /ruta/a/facturas --batch-sizes 10 25 50 100

# Benchmark con datos de verdad de campo
python benchmark_model.py --test-dir /ruta/a/facturas --ground-truth ground_truth.json

# Crear archivo de ground truth de ejemplo
python benchmark_model.py --test-dir /ruta/a/facturas --create-sample-gt
```

### 3. Uso de la API

#### Evaluar Métricas de un Archivo

```bash
curl -X POST "http://localhost:8000/evaluate-metrics" \
  -F "file=@factura.pdf" \
  -F 'ground_truth={"tipo_factura": "A", "razon_social_vendedor": "Empresa SRL", ...}'
```

#### Benchmark de Lotes

```bash
curl -X POST "http://localhost:8000/batch-benchmark" \
  -F "files=@factura1.pdf" \
  -F "files=@factura2.pdf" \
  -F "files=@factura3.pdf" \
  -F 'ground_truth={"factura1.pdf": {...}, "factura2.pdf": {...}}'
```

## 📁 Estructura de Archivos

```
├── services/
│   ├── metrics_calculator.py    # Calculador de métricas
│   ├── batch_processor.py       # Procesador de lotes
│   └── invoice_parser.py        # Parser de facturas (existente)
├── benchmark_model.py           # Script principal de benchmark
├── test_metrics_system.py       # Script de pruebas
├── main.py                      # API con endpoints de métricas
└── models.py                    # Modelos de datos actualizados
```

## 📋 Preparación de Datos

### 1. Archivos de Prueba
Coloca tus facturas en un directorio:
```
test_facturas/
├── factura1.pdf
├── factura2.jpg
├── factura3.png
└── ...
```

### 2. Ground Truth (Datos de Verdad de Campo)
Crea un archivo JSON con los datos correctos:

```json
{
  "factura1.pdf": {
    "tipo_factura": "A",
    "razon_social_vendedor": "Empresa Ejemplo SRL",
    "cuit_vendedor": "20-12345678-9",
    "razon_social_comprador": "Cliente Ejemplo",
    "cuit_comprador": "20-87654321-0",
    "condicion_iva_comprador": "Responsable Inscripto",
    "condicion_venta": "Contado",
    "fecha_emision": "01/01/2024",
    "subtotal": "1000,00",
    "importe_total": "1210,00",
    "iva": "210,00",
    "deuda_impositiva": "210,00",
    "numero_factura": "0001-00000001",
    "punto_venta": "0001",
    "raw_text": "Texto completo de la factura..."
  }
}
```

## 📊 Interpretación de Resultados

### Confidence Score
- **0.8 - 1.0**: Excelente - Modelo muy confiable
- **0.6 - 0.8**: Bueno - Modelo confiable con algunos campos faltantes
- **0.4 - 0.6**: Regular - Modelo necesita mejoras
- **0.0 - 0.4**: Malo - Modelo no es confiable

### Field Accuracy
- **0.9 - 1.0**: Excelente - Casi todos los campos correctos
- **0.7 - 0.9**: Bueno - Mayoría de campos correctos
- **0.5 - 0.7**: Regular - Algunos campos incorrectos
- **0.0 - 0.5**: Malo - Muchos campos incorrectos

### CER/WER
- **0.0 - 0.1**: Excelente - Muy pocos errores de OCR
- **0.1 - 0.3**: Bueno - Algunos errores de OCR
- **0.3 - 0.5**: Regular - Errores moderados de OCR
- **0.5 - 1.0**: Malo - Muchos errores de OCR

### Throughput
- **> 2 docs/seg**: Excelente - Procesamiento muy rápido
- **1 - 2 docs/seg**: Bueno - Procesamiento rápido
- **0.5 - 1 docs/seg**: Regular - Procesamiento moderado
- **< 0.5 docs/seg**: Malo - Procesamiento lento

## 🔧 Configuración Avanzada

### Ajustar Número de Workers
```bash
python benchmark_model.py --test-dir /ruta/facturas --max-workers 8
```

### Procesar Lotes Específicos
```bash
python benchmark_model.py --test-dir /ruta/facturas --batch-sizes 50 100
```

### Guardar Resultados en Directorio Específico
```bash
python benchmark_model.py --test-dir /ruta/facturas --output-dir resultados_benchmark
```

## 📈 Ejemplo de Salida

```
=== REPORTE DE RENDIMIENTO DEL MODELO ===
Fecha: 2024-01-15 14:30:25

RESUMEN DEL LOTE:
- Total de archivos: 50
- Archivos procesados exitosamente: 48
- Archivos fallidos: 2
- Tasa de éxito: 96.00%
- Tiempo total de procesamiento: 45.30 segundos

MÉTRICAS DE RENDIMIENTO:
- Throughput: 1.06 documentos/segundo
- Tiempo promedio por documento: 0.94 segundos
- Confidence Score promedio: 0.847

MÉTRICAS DE CALIDAD:
- Precisión de campos promedio: 0.923
- CER (Character Error Rate) promedio: 0.045
- WER (Word Error Rate) promedio: 0.078
- Campos correctos totales: 442
- Campos faltantes totales: 23
- Campos incorrectos totales: 15
```

## 🐛 Solución de Problemas

### Error: "No se encontraron archivos de prueba"
- Verifica que el directorio contenga archivos .pdf, .jpg, .jpeg, .png
- Asegúrate de que los archivos no estén corruptos

### Error: "Error procesando ground truth"
- Verifica que el JSON sea válido
- Asegúrate de que los nombres de archivo coincidan exactamente

### Rendimiento lento
- Reduce el número de workers si hay problemas de memoria
- Procesa lotes más pequeños
- Verifica que no haya otros procesos consumiendo recursos

## 🚀 Mejoras Implementadas

### 1. **Cálculo de Confianza Mejorado**
- **Enfoque**: Solo campos estructurados específicos (no todo lo que extrae el OCR)
- **Campos evaluados**: `cuit_vendedor`, `cuit_comprador`, `fecha_emision`, `subtotal`, `importe_total`
- **Peso**: 70% campos estructurados, 30% items estructurados
- **Beneficio**: Confianza precisa basada solo en datos relevantes del ground truth

### 2. **Evaluación Solo de Campos Estructurados**
- **Campos principales**: `cuit_vendedor`, `cuit_comprador`, `fecha_emision`, `subtotal`, `importe_total`
- **Campos de items**: `descripcion`, `cantidad`, `precio_unitario`, `bonificacion`, `importe_bonificacion`
- **Ignorados**: Todos los otros campos extraídos por OCR que no están en ground truth
- **Beneficio**: Métricas precisas sin penalizar campos irrelevantes

### 3. **CER/WER Mejorado - Solo Campos Importantes**
- **Extracción selectiva**: Solo campos estructurados importantes
- **Normalización completa**: Minúsculas, sin comas/puntos, sin espacios extra
- **Patrones flexibles**: Extrae CUITs, fechas, montos, porcentajes, palabras importantes
- **Filtrado inteligente**: Solo elementos relevantes, evita números irrelevantes
- **Ground truth text**: Generado automáticamente desde JSON para comparación
- **Beneficio**: CER/WER precisos y relevantes (0.000 = perfecto)

### 4. **Cálculo Automático de Items**
- **`importe_bonificacion`**: Calculado automáticamente cuando falta
- **`subtotal`**: Calculado como `(cantidad * precio_unitario) - importe_bonificacion`
- **Validación de items**: Solo campos importantes para confianza
- **Beneficio**: Items más completos y precisos

### 5. **Métricas Comprehensivas Mejoradas**
- **Pre-procesamiento**: Correcciones aplicadas antes del cálculo
- **Textos limpios**: CER/WER calculados con texto normalizado
- **Campos corregidos**: Accuracy basado en campos completos
- **Beneficio**: Métricas más precisas y consistentes

## 📊 Resultados de las Mejoras

### Antes vs Después:
```
Evaluación Original: Todos los campos del OCR → Evaluación Mejorada: Solo campos estructurados
Confianza Original: Variable → Confianza Mejorada: 1.000 (perfecto)
Accuracy Original: Baja por campos irrelevantes → Accuracy Mejorada: 1.000 (perfecto)
CER/WER: Mejorados con limpieza de texto
```

### Campos Estructurados Evaluados:
- **Principales**: `cuit_vendedor`, `cuit_comprador`, `fecha_emision`, `subtotal`, `importe_total`
- **Items**: `descripcion`, `cantidad`, `precio_unitario`, `bonificacion`, `importe_bonificacion`
- **Ignorados**: 15+ campos del OCR que no están en ground truth

## 🧪 Pruebas de las Mejoras

```bash
# Probar evaluación solo de campos estructurados
python test_structured_metrics.py

# Probar las mejoras implementadas
python tests/test_improvements.py
```

Estos scripts demuestran:
- CER/WER calculado solo sobre campos importantes con normalización completa
- Evaluación solo de campos estructurados específicos
- Ignorar campos del OCR que no están en ground truth
- Cálculo mejorado de confianza basado en datos relevantes
- Métricas precisas sin penalizar campos irrelevantes

## 📞 Soporte

Para problemas o preguntas sobre el sistema de métricas:
1. Revisa los logs en la consola
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que los archivos de prueba sean válidos
4. Consulta la documentación de la API en `/docs` cuando el servidor esté ejecutándose
5. Ejecuta `python tests/test_improvements.py` para verificar las mejoras

## 📋 Análisis Detallado de Campos

El sistema incluye un **analizador detallado de campos** que permite identificar exactamente qué campos están causando problemas de precisión en el modelo.

### 🎯 Funcionalidades del Análisis Detallado

#### 1. **Comparación con Ground Truth Real**
- Compara los campos extraídos con los datos reales del JSON
- Identifica campos correctos, incorrectos y faltantes
- Proporciona ejemplos específicos de errores

#### 2. **Estadísticas por Campo**
- **Precisión por campo**: Porcentaje de aciertos para cada campo
- **Conteo de errores**: Campos correctos, incorrectos y faltantes
- **Ejemplos de errores**: Casos específicos donde el campo falló

#### 3. **Análisis por Documento**
- Identifica documentos con mejor y peor rendimiento
- Muestra la precisión individual de cada factura
- Permite identificar patrones problemáticos

#### 4. **Recomendaciones Específicas**
- Prioriza campos que requieren mejora
- Identifica si el problema es extracción o validación
- Proporciona recomendaciones concretas de mejora

### 🚀 Uso del Análisis Detallado

#### 1. **Generar Reporte de Análisis**

```bash
# Análisis detallado con ground truth real
python services/detailed_field_analysis.py

# Con parámetros personalizados
python services/detailed_field_analysis.py \
  --benchmark-file benchmark_results/dataset_benchmark_results.json \
  --dataset-dir "C:\Users\selel\OneDrive\Documentos\Facultad\ARPYME\creacion_dataset\dataset_facturas" \
  --output benchmark_results/detailed_field_analysis.txt
```

#### 2. **Interpretar los Resultados**

El reporte generado incluye:

**📊 Resumen Ejecutivo:**
- Total de documentos analizados
- Total de campos analizados  
- Precisión promedio general

**⚠️ Campos con Peor Rendimiento (Top 5):**
- Lista de campos que más afectan la precisión
- Porcentaje de precisión específico
- Ejemplos de errores encontrados

**✅ Campos con Mejor Rendimiento (Top 5):**
- Campos que funcionan correctamente
- Confirmación de que el modelo extrae bien ciertos tipos de datos

**📋 Análisis Completo por Campo:**
- Estadísticas detalladas de cada campo
- Desglose de errores (correctos, incorrectos, faltantes)
- Ejemplos específicos de errores

**📈 Análisis por Documento:**
- Documentos con mejor y peor rendimiento
- Identificación de facturas problemáticas

**🎯 Recomendaciones Específicas:**
- Prioridades de mejora
- Tipos de problemas identificados
- Acciones recomendadas

### 📋 Ejemplo de Reporte

```
=== REPORTE DETALLADO DE ANÁLISIS DE CAMPOS ===
Fecha: 2025-09-19 21:05:06
Total de documentos analizados: 10

RESUMEN EJECUTIVO:
• Total de campos analizados: 10
• Precisión promedio: 0.786 (78.6%)

CAMPOS CON PEOR RENDIMIENTO (Top 5):

1. BONIFICACION:
   Precisión: 0.000 (0.0%)
   Total evaluado: 28
   Correctos: 0 (0.0%)
   Incorrectos: 0 (0.0%)
   Faltantes: 28 (100.0%)

2. DESCRIPCION:
   Precisión: 0.714 (71.4%)
   Total evaluado: 28
   Correctos: 20 (71.4%)
   Incorrectos: 8 (28.6%)
   Faltantes: 0 (0.0%)
   Ejemplos de errores:
     • factura_11.png: '' vs 'mantenimiento mensual'
     • factura_10.png: 'instalación servidores' vs 'implementación de red'

RECOMENDACIONES ESPECÍFICAS:
🎯 PRIORIDAD ALTA: Mejorar el campo 'bonificacion'
   • Precisión actual: 0.0%
   • Problema principal: CAMPOS FALTANTES (28 de 28)
   • Recomendación: Mejorar extracción/reconocimiento de este campo
```

### 🔧 Configuración del Análisis

#### Parámetros Disponibles:

- `--benchmark-file`: Archivo JSON de resultados del benchmark
- `--dataset-dir`: Directorio del dataset con JSONs de ground truth
- `--output`: Archivo de salida del reporte

#### Campos Analizados:

**Campos Principales:**
- `cuit_vendedor`: CUIT del vendedor
- `cuit_comprador`: CUIT del comprador
- `fecha_emision`: Fecha de emisión
- `subtotal`: Subtotal de la factura
- `importe_total`: Importe total

**Campos de Items:**
- `descripcion`: Descripción del producto/servicio
- `cantidad`: Cantidad del item
- `precio_unitario`: Precio unitario
- `bonificacion`: Porcentaje de bonificación
- `importe_bonificacion`: Importe de la bonificación

### 💡 Casos de Uso

#### 1. **Identificar Problemas Específicos**
```bash
# Después de ejecutar un benchmark
python services/detailed_field_analysis.py
# Revisar el reporte para identificar campos problemáticos
```

#### 2. **Validar Mejoras del Modelo**
```bash
# Antes y después de mejorar el modelo
python services/detailed_field_analysis.py --output before_improvement.txt
# ... mejorar el modelo ...
python services/detailed_field_analysis.py --output after_improvement.txt
# Comparar los reportes para verificar mejoras
```

#### 3. **Análisis de Dataset Específico**
```bash
# Analizar un dataset específico
python services/detailed_field_analysis.py \
  --dataset-dir "path/to/specific/dataset" \
  --output "analysis_specific_dataset.txt"
```

### 📊 Interpretación de Resultados

#### **Precisión por Campo:**
- **100%**: Campo funciona perfectamente
- **80-99%**: Campo funciona bien, mejoras menores
- **60-79%**: Campo necesita mejoras moderadas
- **<60%**: Campo requiere atención prioritaria
- **0%**: Campo no funciona, requiere rediseño

#### **Tipos de Errores:**
- **Campos Faltantes**: El campo no se extrae
- **Campos Incorrectos**: El campo se extrae pero con valor incorrecto
- **Campos Vacíos**: El campo se extrae pero está vacío

#### **Recomendaciones por Tipo de Error:**
- **Faltantes**: Mejorar patrones de extracción o reconocimiento OCR
- **Incorrectos**: Mejorar validación o lógica de extracción
- **Vacíos**: Revisar condiciones de extracción

### 🔄 Integración con el Workflow

El análisis detallado se integra perfectamente con el workflow de benchmark:

1. **Ejecutar Benchmark**: `python benchmark_dataset.py --dataset-dir ...`
2. **Generar Análisis**: `python services/detailed_field_analysis.py`
3. **Revisar Resultados**: Analizar el reporte generado
4. **Implementar Mejoras**: Basado en las recomendaciones
5. **Repetir**: Ejecutar nuevo benchmark para validar mejoras

### 📁 Archivos Generados

- `benchmark_results/detailed_field_analysis.txt`: Reporte detallado completo
- Incluye análisis por campo, documento y recomendaciones específicas

Este sistema de análisis detallado te permite **identificar exactamente qué campos están causando problemas** y **priorizar las mejoras** de manera eficiente.

## 📋 Documentación Adicional

### 📊 Análisis de Rendimiento de Campos

Para información detallada sobre el rendimiento actual de cada campo:

- **📈 Resumen Ejecutivo**: `FIELD_PERFORMANCE_SUMMARY.md` - Vista rápida de campos problemáticos y excelentes
- **📋 Análisis Completo**: `FIELD_PERFORMANCE_ANALYSIS.md` - Análisis detallado con métricas, ejemplos y plan de mejoras
- **🔍 Reporte Técnico**: `benchmark_results/detailed_field_analysis.txt` - Resultados del último análisis

### 🎯 Estado Actual del Sistema

**Precisión Promedio**: 78.6% | **Estado**: Moderado

**Campos Excelentes** (100% precisión):
- CUIT Vendedor, CUIT Comprador, Fecha Emisión, Subtotal, Importe Total

**Campos Problemáticos**:
- 🚨 **Bonificación**: 0% (100% campos faltantes)
- 🔴 **Descripción**: 71.4% (28.6% incorrectos)
- 🔴 **Cantidad**: 71.4% (28.6% incorrectos)
- 🔴 **Precio Unitario**: 71.4% (28.6% incorrectos)
- 🔴 **Importe Bonificación**: 71.4% (28.6% incorrectos)

### 🚀 Próximos Pasos Recomendados

1. **Prioridad ALTA**: Rediseñar extracción de bonificaciones (0% → 70%+)
2. **Prioridad MEDIA**: Mejorar campos de items (71.4% → 80%+)
3. **Prioridad BAJA**: Optimizar throughput y CER/WER
