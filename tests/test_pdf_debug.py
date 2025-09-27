#!/usr/bin/env python3
"""
Script para debuggear el procesamiento de PDFs
"""
import sys
sys.path.append('.')
from services.advanced_image_processor import AdvancedImageProcessor
from services.invoice_parser import InvoiceParser

def test_pdf_processing():
    """Probar el procesamiento del PDF de ejemplo"""
    try:
        # Probar con el PDF de ejemplo
        processor = AdvancedImageProcessor()
        result = processor.process_image('factura_2.pdf')

        print('=== RESULTADO DEL PROCESAMIENTO ===')
        print(f'Status: {result.status}')
        print(f'Filename: {result.filename}')
        print(f'Processing time: {result.processing_time:.2f}s')
        print(f'Raw text length: {len(result.raw_text)}')
        print(f'Text blocks: {len(result.text_blocks)}')
        print(f'Tables: {len(result.tables)}')
        print(f'Figures: {len(result.figures)}')

        print('\n=== METADATA ===')
        print(f'Layout elements: {result.metadata.get("layout_elements_count", 0)}')
        print(f'Is PDF: {result.metadata.get("is_pdf", False)}')
        print(f'Processor: {result.metadata.get("processor", "unknown")}')

        print('\n=== INVOICE PARSING ===')
        invoice_data = result.metadata.get('invoice_parsing', {})
        print(f'Success: {invoice_data.get("success", False)}')
        print(f'Total invoices: {invoice_data.get("total_invoices", 0)}')
        print(f'Invoices: {len(invoice_data.get("invoices", []))}')

        if invoice_data.get('invoices'):
            for i, invoice in enumerate(invoice_data['invoices']):
                print(f'\nInvoice {i+1}:')
                print(f'  Success: {invoice.get("success", False)}')
                print(f'  Confidence: {invoice.get("parsing_confidence", 0):.2f}')
                print(f'  Fields: {list(invoice.get("extracted_fields", {}).keys())}')
                
                # Mostrar algunos campos extraídos
                extracted_fields = invoice.get("extracted_fields", {})
                if extracted_fields:
                    print(f'  Sample fields:')
                    for key, value in list(extracted_fields.items())[:5]:
                        print(f'    {key}: {value}')

        print('\n=== RAW TEXT SAMPLE ===')
        print(result.raw_text[:500] + '...' if len(result.raw_text) > 500 else result.raw_text)
        
        # Probar el parser directamente
        print('\n=== TESTING PARSER DIRECTLY ===')
        parser = InvoiceParser()
        direct_result = parser.parse_multiple_invoices(result.raw_text)
        print(f'Direct parser success: {direct_result.get("success", False)}')
        print(f'Direct parser total invoices: {direct_result.get("total_invoices", 0)}')
        
        return result
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_pdf_processing()
