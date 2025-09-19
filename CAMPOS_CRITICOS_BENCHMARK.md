# 📋 **CAMPOS CRÍTICOS PARA EL BENCHMARK - ACTUALIZADO**

## 🎯 **CAMPOS CRÍTICOS DEFINIDOS**

Según tu especificación, los campos críticos para el benchmark son:

### **🔑 CAMPOS PRINCIPALES CRÍTICOS**
1. **`cuit_vendedor`** - CUIT del vendedor/emisor
2. **`cuit_comprador`** - CUIT del comprador/receptor  
3. **`fecha_emision`** - Fecha de emisión de la factura
4. **`subtotal`** - Subtotal de la factura
5. **`importe_total`** - Importe total de la factura

### **📦 CAMPOS DE ITEMS CRÍTICOS**
Para cada producto/item en la factura, se evalúan **TODOS** estos campos:

1. **`descripcion`** - Descripción del producto/servicio
2. **`cantidad`** - Cantidad del producto
3. **`precio_unitario`** - Precio unitario del producto
4. **`bonificacion`** - Porcentaje de bonificación
5. **`importe_bonificacion`** - Importe de la bonificación

## 📊 **SISTEMA DE EVALUACIÓN ACTUALIZADO**

### **Pesos de Evaluación:**
- **Campos críticos principales**: 60% del score
- **Items (todos los campos)**: 30% del score  
- **Campos adicionales**: 10% del score

### **Cálculo de Accuracy:**
```
Accuracy = (Campos críticos correctos + Items correctos) / Total de campos evaluados
```

## 🗂️ **ESTRUCTURA JSON PARA EL DATASET**

### **Ejemplo Completo con Campos Críticos:**

```json
{
    "cuit_vendedor": "30-99999999-7",
    "cuit_comprador": "20-12345678-9", 
    "fecha_emision": "27/04/2025",
    "subtotal": "34.130,00",
    "importe_total": "43.239,30",
    "productos": [
        {
            "descripcion": "Soporte técnico",
            "cantidad": 5,
            "precio_unitario": 2000,
            "bonificacion": 15,
            "importe_bonificacion": 300.0
        },
        {
            "descripcion": "Licencia software", 
            "cantidad": 2,
            "precio_unitario": 3000,
            "bonificacion": 7,
            "importe_bonificacion": 210.0
        }
    ]
}
```

## ⚠️ **IMPORTANTE PARA EL BENCHMARK**

### **Campos Obligatorios en cada JSON:**
- ✅ `cuit_vendedor` (formato: XX-XXXXXXXX-X)
- ✅ `cuit_comprador` (formato: XX-XXXXXXXX-X)  
- ✅ `fecha_emision` (formato: DD/MM/YYYY)
- ✅ `subtotal` (formato argentino: XX.XXX,XX)
- ✅ `importe_total` (formato argentino: XX.XXX,XX)
- ✅ `productos` (array con al menos 1 item)

### **Para cada item en `productos`:**
- ✅ `descripcion` (texto descriptivo)
- ✅ `cantidad` (número entero)
- ✅ `precio_unitario` (número)
- ✅ `bonificacion` (número entero, porcentaje)
- ✅ `importe_bonificacion` (número decimal)

## 🎯 **CAMPOS ADICIONALES (NO CRÍTICOS)**

Estos campos se evalúan pero con menor peso:

```json
{
    "tipo_factura": "A",
    "razon_social_vendedor": "Digital Future Ltda",
    "razon_social_comprador": "Laura Gómez",
    "numero_factura": "13225316",
    "punto_venta": "0004",
    "condicion_iva_comprador": "Monotributista",
    "condicion_venta": "Contado",
    "iva": "7.167,30",
    "deuda_impositiva": "9.109,30"
}
```

## 📈 **MÉTRICAS DEL BENCHMARK**

El sistema ahora calcula:

1. **Accuracy de campos críticos** (cuit_vendedor, cuit_comprador, fecha_emision, subtotal, importe_total)
2. **Accuracy de items** (descripcion, cantidad, precio_unitario, bonificacion, importe_bonificacion)
3. **Accuracy total** (combinación ponderada)
4. **CER y WER** (Character/Word Error Rate)
5. **Throughput** (documentos por segundo)
6. **Confidence Score** (basado en campos críticos e items)

## 💡 **CONSEJOS PARA CREAR EL DATASET**

1. **Asegúrate de incluir los 5 campos críticos principales** en cada JSON
2. **Incluye al menos 1 producto** con todos los campos de items
3. **Usa formatos consistentes** (especialmente fechas y números)
4. **Variedad de datos**: Diferentes CUITs, fechas, montos, productos
5. **Nombres de archivo**: `factura_1.png` y `factura_1.json`

## 🚀 **COMANDO PARA EJECUTAR EL BENCHMARK**

```bash
python benchmark_dataset.py --dataset-dir "C:\Users\selel\OneDrive\Documentos\Facultad\ARPYME\creacion_dataset\dataset_facturas" --batch-sizes 10 20 30 50 --output-dir benchmark_results
```

El benchmark ahora evaluará específicamente estos campos críticos y te dará métricas detalladas sobre la precisión del modelo en la extracción de CUITs, fechas, montos y todos los datos de los productos.
