from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from typing import Dict, Any, List
import logging

# Aplicar parche de compatibilidad para Pillow
try:
    from PIL import Image
    if not hasattr(Image, 'LINEAR'):
        Image.LINEAR = Image.Resampling.LANCZOS
    if not hasattr(Image, 'BILINEAR'):
        Image.BILINEAR = Image.Resampling.BILINEAR
    if not hasattr(Image, 'NEAREST'):
        Image.NEAREST = Image.Resampling.NEAREST
except ImportError:
    pass

from config import settings
from models import ProcessingResult, ErrorResponse, StructuredInvoiceResponse, InvoiceFields, MetricsData, BatchMetrics
from services.advanced_image_processor import AdvancedImageProcessor
from services.metrics_calculator import MetricsCalculator
from services.batch_processor import BatchProcessor
from utils.file_utils import validate_file_type, validate_file_size, save_upload_file, cleanup_file

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Configurar CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Crear directorio para archivos temporales si no existe
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)

# Inicializar procesador avanzado de imágenes con scikit-image
image_processor = AdvancedImageProcessor()

# Inicializar calculador de métricas y procesador de lotes
metrics_calculator = MetricsCalculator()
batch_processor = BatchProcessor()

@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "message": "API de Procesamiento de Imágenes con OCR",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "process_image": "/process-image (INTELIGENTE - detecta facturas automáticamente)",
            "process_multiple_images": "/process-multiple-images (INTELIGENTE - múltiples archivos)",
            "process_invoice": "/process-invoice (solo facturas)",
            "process_invoices_structured": "/process-invoices-structured (solo facturas estructuradas)",
            "evaluate_metrics": "/evaluate-metrics (evaluar métricas del modelo)",
            "batch_benchmark": "/batch-benchmark (benchmark de lotes)"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "healthy", "message": "API funcionando correctamente"}

@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    """
    Endpoint inteligente para procesar imágenes - detecta automáticamente si es una factura
    y extrae datos estructurados o texto general según corresponda
    
    Args:
        file: Archivo de imagen/PDF a procesar
        
    Returns:
        JSON con datos estructurados si es factura, o texto extraído si es imagen general
    """
    file_path = None
    try:
        # Validar tipo de archivo
        if not validate_file_type(file, settings.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Validar tamaño de archivo
        if not validate_file_size(file, settings.MAX_FILE_SIZE):
            raise HTTPException(
                status_code=400,
                detail=f"Archivo demasiado grande. Tamaño máximo: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Guardar archivo temporalmente
        file_path = save_upload_file(file, settings.UPLOAD_DIR)
        if not file_path:
            raise HTTPException(
                status_code=500,
                detail="Error guardando archivo temporal"
            )
        
        logger.info(f"Procesando archivo: {file_path}")
        
        # Procesar imagen con LayoutParser y Tesseract
        result = image_processor.process_image(file_path)
        
        # Detectar si es una factura y extraer datos estructurados
        invoice_data = result.metadata.get("invoice_parsing", {})
        
        if invoice_data.get("success", False) and invoice_data.get("total_invoices", 0) > 0:
            # Es una factura - retornar datos estructurados
            invoices = invoice_data.get("invoices", [])
            structured_invoices = []
            
            for i, invoice in enumerate(invoices):
                if invoice.get("success", False):
                    extracted_fields = invoice.get("extracted_fields", {})
                    
                    # Crear objeto InvoiceFields
                    invoice_fields = InvoiceFields(
                        # Campos principales según modelo Django
                        tipo_factura=extracted_fields.get("tipo_factura"),
                        razon_social_vendedor=extracted_fields.get("razon_social_vendedor"),
                        cuit_vendedor=extracted_fields.get("cuit_vendedor"),
                        razon_social_comprador=extracted_fields.get("razon_social_comprador"),
                        cuit_comprador=extracted_fields.get("cuit_comprador"),
                        condicion_iva_comprador=extracted_fields.get("condicion_iva_comprador"),
                        condicion_venta=extracted_fields.get("condicion_venta"),
                        fecha_emision=extracted_fields.get("fecha_emision"),
                        subtotal=extracted_fields.get("subtotal"),
                        deuda_impositiva=extracted_fields.get("deuda_impositiva"),
                        importe_total=extracted_fields.get("importe_total"),
                        
                        # Campos adicionales útiles
                        numero_factura=extracted_fields.get("numero_factura"),
                        punto_venta=extracted_fields.get("punto_venta"),
                        
                        # Items de la factura
                        items=extracted_fields.get("items")
                    )
                    
                    # Crear respuesta estructurada para esta factura
                    structured_invoice = {
                        "invoice_index": i + 1,
                        "invoice_fields": invoice_fields.dict(),
                        "raw_text": invoice.get("raw_text", ""),
                        "parsing_confidence": invoice.get("parsing_confidence", 0.0),
                        "status": "success"
                    }
                    
                    structured_invoices.append(structured_invoice)
            
            # Retornar respuesta estructurada para facturas
            return {
                "type": "invoice",
                "success": True,
                "filename": result.filename,
                "file_size": result.file_size,
                "content_type": result.content_type,
                "processing_time": result.processing_time,
                "total_invoices": len(structured_invoices),
                "invoices": structured_invoices,
                "metadata": {
                    "layout_elements_count": result.metadata.get("layout_elements_count", 0),
                    "text_blocks_count": result.metadata.get("text_blocks_count", 0),
                    "tables_count": result.metadata.get("tables_count", 0),
                    "figures_count": result.metadata.get("figures_count", 0),
                    "is_pdf": result.metadata.get("is_pdf", False),
                    "processor": result.metadata.get("processor", "scikit-image")
                }
            }
        else:
            # No es una factura - retornar datos generales de OCR
            return {
                "type": "general_text",
                "success": True,
                "filename": result.filename,
                "file_size": result.file_size,
                "content_type": result.content_type,
                "processing_time": result.processing_time,
                "raw_text": result.raw_text,
                "text_blocks": [block.dict() for block in result.text_blocks],
                "tables": [table.dict() for table in result.tables],
                "figures": [figure.dict() for figure in result.figures],
                "metadata": result.metadata
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando imagen: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
    finally:
        # Limpiar archivo temporal
        if file_path and os.path.exists(file_path):
            cleanup_file(file_path)

@app.post("/process-invoice", response_model=StructuredInvoiceResponse)
async def process_invoice(file: UploadFile = File(...)):
    """
    Endpoint para procesar facturas y extraer campos específicos
    
    Args:
        file: Archivo de imagen/PDF de factura a procesar
        
    Returns:
        JSON con campos estructurados de la factura
    """
    file_path = None
    try:
        # Validar tipo de archivo
        if not validate_file_type(file, settings.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Validar tamaño de archivo
        if not validate_file_size(file, settings.MAX_FILE_SIZE):
            raise HTTPException(
                status_code=400,
                detail=f"Archivo demasiado grande. Tamaño máximo: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Guardar archivo temporalmente
        file_path = save_upload_file(file, settings.UPLOAD_DIR)
        if not file_path:
            raise HTTPException(
                status_code=500,
                detail="Error guardando archivo temporal"
            )
        
        logger.info(f"Procesando factura: {file_path}")
        
        # Procesar imagen con LayoutParser y Tesseract
        result = image_processor.process_image(file_path)
        
        # Extraer datos de la factura
        invoice_data = result.metadata.get("invoice_parsing", {})
        
        if invoice_data.get("success", False):
            extracted_fields = invoice_data.get("extracted_fields", {})
            
            # Crear objeto InvoiceFields
            invoice_fields = InvoiceFields(
                # Campos principales según modelo Django
                tipo_factura=extracted_fields.get("tipo_factura"),
                razon_social_vendedor=extracted_fields.get("razon_social_vendedor"),
                cuit_vendedor=extracted_fields.get("cuit_vendedor"),
                razon_social_comprador=extracted_fields.get("razon_social_comprador"),
                cuit_comprador=extracted_fields.get("cuit_comprador"),
                condicion_iva_comprador=extracted_fields.get("condicion_iva_comprador"),
                condicion_venta=extracted_fields.get("condicion_venta"),
                fecha_emision=extracted_fields.get("fecha_emision"),
                subtotal=extracted_fields.get("subtotal"),
                deuda_impositiva=extracted_fields.get("deuda_impositiva"),
                importe_total=extracted_fields.get("importe_total"),
                
                # Campos adicionales útiles
                numero_factura=extracted_fields.get("numero_factura"),
                punto_venta=extracted_fields.get("punto_venta"),
                
                # Items de la factura
                items=extracted_fields.get("items")
            )
        else:
            # Si falla el parsing, crear campos vacíos
            invoice_fields = InvoiceFields()
        
        # Crear respuesta estructurada
        structured_response = StructuredInvoiceResponse(
            filename=result.filename,
            file_size=result.file_size,
            content_type=result.content_type,
            processing_time=result.processing_time,
            status=result.status,
            invoice_fields=invoice_fields,
            raw_text=result.raw_text,
            text_blocks=result.text_blocks,
            metadata=result.metadata,
            error_message=result.error_message
        )
        
        return structured_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando factura: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
    finally:
        # Limpiar archivo temporal
        if file_path and os.path.exists(file_path):
            cleanup_file(file_path)

@app.post("/process-multiple-images")
async def process_multiple_images(files: List[UploadFile] = File(...)):
    """
    Endpoint inteligente para procesar múltiples archivos - detecta automáticamente 
    si son facturas y extrae datos estructurados o texto general según corresponda
    
    Args:
        files: Lista de archivos de imágenes/PDFs a procesar
        
    Returns:
        JSON con resultados estructurados para facturas o texto general para otros archivos
    """
    all_results = []
    file_paths = []
    
    try:
        # Validar que se envíen archivos
        if not files:
            raise HTTPException(status_code=400, detail="No se enviaron archivos")
        
        # Validar límite de archivos
        if len(files) > 10:  # Límite de 10 archivos
            raise HTTPException(status_code=400, detail="Máximo 10 archivos permitidos")
        
        processor = AdvancedImageProcessor()
        
        for i, file in enumerate(files):
            file_path = None
            try:
                # Validar tipo de archivo
                if not validate_file_type(file, settings.ALLOWED_EXTENSIONS):
                    all_results.append({
                        "file_index": i + 1,
                        "filename": file.filename,
                        "type": "error",
                        "success": False,
                        "error": f"Tipo de archivo no permitido: {file.content_type}"
                    })
                    continue
                
                # Validar tamaño
                if not validate_file_size(file, settings.MAX_FILE_SIZE):
                    all_results.append({
                        "file_index": i + 1,
                        "filename": file.filename,
                        "type": "error",
                        "success": False,
                        "error": f"Archivo demasiado grande: {file.size} bytes"
                    })
                    continue
                
                # Guardar archivo temporal
                file_path = save_upload_file(file, settings.UPLOAD_DIR)
                file_paths.append(file_path)
                
                # Procesar archivo
                result = processor.process_image(file_path)
                
                # Detectar si es una factura y extraer datos estructurados
                invoice_data = result.metadata.get("invoice_parsing", {})
                
                if invoice_data.get("success", False) and invoice_data.get("total_invoices", 0) > 0:
                    # Es una factura - retornar datos estructurados
                    invoices = invoice_data.get("invoices", [])
                    structured_invoices = []
                    
                    for j, invoice in enumerate(invoices):
                        if invoice.get("success", False):
                            extracted_fields = invoice.get("extracted_fields", {})
                            
                            # Crear objeto InvoiceFields
                            invoice_fields = InvoiceFields(
                                # Campos principales según modelo Django
                                tipo_factura=extracted_fields.get("tipo_factura"),
                                razon_social_vendedor=extracted_fields.get("razon_social_vendedor"),
                                cuit_vendedor=extracted_fields.get("cuit_vendedor"),
                                razon_social_comprador=extracted_fields.get("razon_social_comprador"),
                                cuit_comprador=extracted_fields.get("cuit_comprador"),
                                condicion_iva_comprador=extracted_fields.get("condicion_iva_comprador"),
                                condicion_venta=extracted_fields.get("condicion_venta"),
                                fecha_emision=extracted_fields.get("fecha_emision"),
                                subtotal=extracted_fields.get("subtotal"),
                                deuda_impositiva=extracted_fields.get("deuda_impositiva"),
                                importe_total=extracted_fields.get("importe_total"),
                                
                                # Campos adicionales útiles
                                numero_factura=extracted_fields.get("numero_factura"),
                                punto_venta=extracted_fields.get("punto_venta"),
                                
                                # Items de la factura
                                items=extracted_fields.get("items")
                            )
                            
                            # Crear respuesta estructurada para esta factura
                            structured_invoice = {
                                "invoice_index": j + 1,
                                "invoice_fields": invoice_fields.dict(),
                                "raw_text": invoice.get("raw_text", ""),
                                "parsing_confidence": invoice.get("parsing_confidence", 0.0),
                                "status": "success"
                            }
                            
                            structured_invoices.append(structured_invoice)
                    
                    # Agregar resultado de factura
                    all_results.append({
                        "file_index": i + 1,
                        "filename": result.filename,
                        "type": "invoice",
                        "success": True,
                        "file_size": result.file_size,
                        "content_type": result.content_type,
                        "processing_time": result.processing_time,
                        "total_invoices": len(structured_invoices),
                        "invoices": structured_invoices,
                        "metadata": {
                            "layout_elements_count": result.metadata.get("layout_elements_count", 0),
                            "text_blocks_count": result.metadata.get("text_blocks_count", 0),
                            "tables_count": result.metadata.get("tables_count", 0),
                            "figures_count": result.metadata.get("figures_count", 0),
                            "is_pdf": result.metadata.get("is_pdf", False),
                            "processor": result.metadata.get("processor", "scikit-image")
                        }
                    })
                else:
                    # No es una factura - retornar datos generales de OCR
                    all_results.append({
                        "file_index": i + 1,
                        "filename": result.filename,
                        "type": "general_text",
                        "success": True,
                        "file_size": result.file_size,
                        "content_type": result.content_type,
                        "processing_time": result.processing_time,
                        "raw_text": result.raw_text,
                        "text_blocks": [block.dict() for block in result.text_blocks],
                        "tables": [table.dict() for table in result.tables],
                        "figures": [figure.dict() for figure in result.figures],
                        "metadata": result.metadata
                    })
                
            except Exception as e:
                logger.error(f"Error procesando archivo {file.filename}: {e}")
                all_results.append({
                    "file_index": i + 1,
                    "filename": file.filename,
                    "type": "error",
                    "success": False,
                    "error": str(e)
                })
            finally:
                # Limpiar archivo temporal
                if file_path and os.path.exists(file_path):
                    cleanup_file(file_path)
                    if file_path in file_paths:
                        file_paths.remove(file_path)
        
        # Crear respuesta consolidada
        successful_results = [r for r in all_results if r.get("success", False)]
        failed_results = [r for r in all_results if not r.get("success", False)]
        invoice_results = [r for r in successful_results if r.get("type") == "invoice"]
        text_results = [r for r in successful_results if r.get("type") == "general_text"]
        
        # Contar facturas totales
        total_invoices = sum(r.get("total_invoices", 0) for r in invoice_results)
        
        return {
            "success": True,
            "total_files": len(files),
            "successful_files": len(successful_results),
            "failed_files": len(failed_results),
            "invoice_files": len(invoice_results),
            "text_files": len(text_results),
            "total_invoices": total_invoices,
            "results": all_results,
            "summary": {
                "total_invoices_found": total_invoices,
                "processing_time_total": sum(r.get("processing_time", 0) for r in successful_results),
                "average_confidence": sum(
                    inv.get("parsing_confidence", 0) 
                    for r in invoice_results 
                    for inv in r.get("invoices", [])
                ) / max(total_invoices, 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Error procesando múltiples archivos: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Limpiar archivos temporales restantes
        for file_path in file_paths:
            if os.path.exists(file_path):
                cleanup_file(file_path)

@app.post("/process-invoices-structured")
async def process_invoices_structured(files: List[UploadFile] = File(...)):
    """
    Endpoint mejorado para procesar múltiples archivos de facturas con datos estructurados
    
    Args:
        files: Lista de archivos de imágenes/PDFs de facturas a procesar
        
    Returns:
        JSON con datos estructurados de todas las facturas encontradas
    """
    all_invoices = []
    file_paths = []
    
    try:
        # Validar que se envíen archivos
        if not files:
            raise HTTPException(status_code=400, detail="No se enviaron archivos")
        
        # Validar límite de archivos
        if len(files) > 10:  # Límite de 10 archivos
            raise HTTPException(status_code=400, detail="Máximo 10 archivos permitidos")
        
        processor = AdvancedImageProcessor()
        
        for i, file in enumerate(files):
            file_path = None
            try:
                # Validar tipo de archivo
                if not validate_file_type(file, settings.ALLOWED_EXTENSIONS):
                    continue
                
                # Validar tamaño
                if not validate_file_size(file, settings.MAX_FILE_SIZE):
                    continue
                
                # Guardar archivo temporal
                file_path = save_upload_file(file, settings.UPLOAD_DIR)
                file_paths.append(file_path)
                
                # Procesar archivo
                result = processor.process_image(file_path)
                
                # Extraer datos de facturas
                invoice_data = result.metadata.get("invoice_parsing", {})
                
                if invoice_data.get("success", False):
                    invoices = invoice_data.get("invoices", [])
                    
                    for j, invoice in enumerate(invoices):
                        if invoice.get("success", False):
                            extracted_fields = invoice.get("extracted_fields", {})
                            
                            # Crear objeto InvoiceFields
                            invoice_fields = InvoiceFields(
                                # Campos principales según modelo Django
                                tipo_factura=extracted_fields.get("tipo_factura"),
                                razon_social_vendedor=extracted_fields.get("razon_social_vendedor"),
                                cuit_vendedor=extracted_fields.get("cuit_vendedor"),
                                razon_social_comprador=extracted_fields.get("razon_social_comprador"),
                                cuit_comprador=extracted_fields.get("cuit_comprador"),
                                condicion_iva_comprador=extracted_fields.get("condicion_iva_comprador"),
                                condicion_venta=extracted_fields.get("condicion_venta"),
                                fecha_emision=extracted_fields.get("fecha_emision"),
                                subtotal=extracted_fields.get("subtotal"),
                                deuda_impositiva=extracted_fields.get("deuda_impositiva"),
                                importe_total=extracted_fields.get("importe_total"),
                                
                                # Campos adicionales útiles
                                numero_factura=extracted_fields.get("numero_factura"),
                                punto_venta=extracted_fields.get("punto_venta"),
                                
                                # Items de la factura
                                items=extracted_fields.get("items")
                            )
                            
                            # Crear respuesta estructurada para esta factura
                            structured_invoice = {
                                "file_index": i + 1,
                                "filename": result.filename,
                                "invoice_index": j + 1,
                                "invoice_fields": invoice_fields.dict(),
                                "raw_text": invoice.get("raw_text", ""),
                                "parsing_confidence": invoice.get("parsing_confidence", 0.0),
                                "processing_time": result.processing_time,
                                "status": "success"
                            }
                            
                            all_invoices.append(structured_invoice)
                
            except Exception as e:
                logger.error(f"Error procesando archivo {file.filename}: {e}")
            finally:
                # Limpiar archivo temporal
                if file_path and os.path.exists(file_path):
                    cleanup_file(file_path)
                    if file_path in file_paths:
                        file_paths.remove(file_path)
        
        return {
            "success": True,
            "total_files": len(files),
            "total_invoices": len(all_invoices),
            "invoices": all_invoices,
            "summary": {
                "files_processed": len([f for f in files if validate_file_type(f, settings.ALLOWED_EXTENSIONS) and validate_file_size(f, settings.MAX_FILE_SIZE)]),
                "total_processing_time": sum(inv.get("processing_time", 0) for inv in all_invoices),
                "average_confidence": sum(inv.get("parsing_confidence", 0) for inv in all_invoices) / len(all_invoices) if all_invoices else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error procesando múltiples archivos: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Limpiar archivos temporales restantes
        for file_path in file_paths:
            if os.path.exists(file_path):
                cleanup_file(file_path)

@app.post("/evaluate-metrics")
async def evaluate_metrics(
    file: UploadFile = File(...),
    ground_truth: str = Form(None)
):
    """
    Endpoint para evaluar métricas del modelo con un archivo y datos de verdad de campo
    
    Args:
        file: Archivo de imagen/PDF de factura a procesar
        ground_truth: JSON string con datos de verdad de campo (opcional)
        
    Returns:
        JSON con métricas de evaluación del modelo
    """
    file_path = None
    try:
        # Validar tipo de archivo
        if not validate_file_type(file, settings.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Validar tamaño de archivo
        if not validate_file_size(file, settings.MAX_FILE_SIZE):
            raise HTTPException(
                status_code=400,
                detail=f"Archivo demasiado grande. Tamaño máximo: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Guardar archivo temporalmente
        file_path = save_upload_file(file, settings.UPLOAD_DIR)
        if not file_path:
            raise HTTPException(
                status_code=500,
                detail="Error guardando archivo temporal"
            )
        
        logger.info(f"Evaluando métricas para archivo: {file_path}")
        
        # Procesar imagen
        result = image_processor.process_image(file_path)
        
        if result.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Error procesando imagen: {result.error_message}"
            )
        
        # Extraer datos de factura
        invoice_data = result.metadata.get("invoice_parsing", {})
        
        if not invoice_data.get("success", False):
            raise HTTPException(
                status_code=400,
                detail="No se pudo extraer datos de factura del archivo"
            )
        
        # Obtener la primera factura
        invoices = invoice_data.get("invoices", [])
        if not invoices:
            raise HTTPException(
                status_code=400,
                detail="No se encontraron facturas en el archivo"
            )
        
        invoice = invoices[0]
        extracted_fields = invoice.get("extracted_fields", {})
        extracted_text = invoice.get("raw_text", "")
        
        # Calcular métricas básicas
        confidence_score = metrics_calculator.calculate_confidence_score(extracted_fields)
        
        # Calcular métricas completas si hay ground truth
        metrics_data = None
        logger.info(f"Ground truth recibido: {ground_truth}")
        logger.info(f"Ground truth type: {type(ground_truth)}")
        logger.info(f"Ground truth bool: {bool(ground_truth)}")
        
        if ground_truth and ground_truth.strip():
            logger.info("Iniciando procesamiento de ground truth...")
            try:
                import json
                logger.info(f"Procesando ground truth: {ground_truth[:100]}...")
                ground_truth_dict = json.loads(ground_truth)
                ground_truth_text = ground_truth_dict.get('raw_text', extracted_text)
                
                logger.info(f"Ground truth dict keys: {list(ground_truth_dict.keys())}")
                logger.info(f"Extracted fields keys: {list(extracted_fields.keys())}")
                
                metrics_result = metrics_calculator.calculate_comprehensive_metrics(
                    extracted_fields=extracted_fields,
                    ground_truth=ground_truth_dict,
                    extracted_text=extracted_text,
                    ground_truth_text=ground_truth_text,
                    processing_time=result.processing_time
                )
                
                logger.info(f"MetricsResult obtenido: {metrics_result}")
                
                metrics_data = MetricsData(
                    confidence_score=metrics_result.confidence_score,
                    field_accuracy=metrics_result.field_accuracy,
                    cer=metrics_result.cer,
                    wer=metrics_result.wer,
                    processing_latency=metrics_result.processing_latency,
                    throughput=metrics_result.throughput,
                    total_fields=metrics_result.total_fields,
                    correct_fields=metrics_result.correct_fields,
                    missing_fields=metrics_result.missing_fields,
                    incorrect_fields=metrics_result.incorrect_fields
                )
                logger.info(f"Métricas calculadas exitosamente: {metrics_data}")
            except Exception as e:
                logger.error(f"Error procesando ground truth: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            logger.info("No hay ground truth o está vacío")
        
        # Crear respuesta
        response = {
            "success": True,
            "filename": result.filename,
            "file_size": result.file_size,
            "processing_time": result.processing_time,
            "confidence_score": confidence_score,
            "extracted_fields": extracted_fields,
            "extracted_text": extracted_text,
            "metrics": metrics_data.model_dump() if metrics_data else None,
            "metadata": {
                "text_blocks_count": len(result.text_blocks),
                "tables_count": len(result.tables),
                "figures_count": len(result.figures),
                "has_ground_truth": ground_truth is not None and ground_truth.strip() != ""
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluando métricas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
    finally:
        # Limpiar archivo temporal
        if file_path and os.path.exists(file_path):
            cleanup_file(file_path)

@app.post("/batch-benchmark")
async def batch_benchmark(
    files: List[UploadFile] = File(...),
    ground_truth: str = None,
    max_workers: int = 4
):
    """
    Endpoint para hacer benchmark de lotes de facturas
    
    Args:
        files: Lista de archivos de imágenes/PDFs de facturas
        ground_truth: JSON string con datos de verdad de campo (opcional)
        max_workers: Número máximo de workers para procesamiento paralelo
        
    Returns:
        JSON con resultados del benchmark del lote
    """
    file_paths = []
    
    try:
        # Validar que se envíen archivos
        if not files:
            raise HTTPException(status_code=400, detail="No se enviaron archivos")
        
        # Validar límite de archivos
        if len(files) > 100:  # Límite de 100 archivos para benchmark
            raise HTTPException(status_code=400, detail="Máximo 100 archivos permitidos para benchmark")
        
        # Guardar archivos temporalmente
        for file in files:
            if validate_file_type(file, settings.ALLOWED_EXTENSIONS) and validate_file_size(file, settings.MAX_FILE_SIZE):
                file_path = save_upload_file(file, settings.UPLOAD_DIR)
                if file_path:
                    file_paths.append(file_path)
        
        if not file_paths:
            raise HTTPException(status_code=400, detail="No se pudieron procesar los archivos")
        
        # Cargar ground truth si se proporciona
        ground_truth_data = None
        if ground_truth:
            try:
                import json
                ground_truth_dict = json.loads(ground_truth)
                # Convertir a formato esperado por batch_processor
                ground_truth_data = {}
                for file in files:
                    if file.filename in ground_truth_dict:
                        ground_truth_data[file.filename] = ground_truth_dict[file.filename]
            except Exception as e:
                logger.warning(f"Error procesando ground truth: {e}")
        
        logger.info(f"Ejecutando benchmark con {len(file_paths)} archivos")
        
        # Ejecutar benchmark
        batch_result = batch_processor.process_batch(
            file_paths=file_paths,
            ground_truth_data=ground_truth_data
        )
        
        # Generar reporte
        report = batch_processor.generate_performance_report(batch_result)
        
        # Crear respuesta
        response = {
            "success": True,
            "batch_info": batch_result['batch_info'],
            "performance_metrics": batch_result['performance_metrics'],
            "report": report,
            "total_files": len(files),
            "processed_files": len(file_paths)
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en benchmark de lote: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
    finally:
        # Limpiar archivos temporales
        for file_path in file_paths:
            if os.path.exists(file_path):
                cleanup_file(file_path)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL,
        workers=1 if settings.DEBUG else settings.WORKERS
    )
