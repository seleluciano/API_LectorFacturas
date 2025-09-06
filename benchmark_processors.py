"""
Script para comparar el rendimiento de diferentes procesadores de imágenes
"""
import time
import os
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

from services.image_processor import ImageProcessor
from services.advanced_image_processor import AdvancedImageProcessor

def benchmark_processors(image_path: str, iterations: int = 3):
    """
    Comparar el rendimiento de diferentes procesadores
    
    Args:
        image_path: Ruta a la imagen de prueba
        iterations: Número de iteraciones para promediar
    """
    if not os.path.exists(image_path):
        print(f"❌ No se encontró la imagen: {image_path}")
        return
    
    print(f"🔍 Comparando procesadores con: {image_path}")
    print(f"📊 Iteraciones: {iterations}")
    print("=" * 60)
    
    # Inicializar procesadores
    pil_processor = ImageProcessor()
    skimage_processor = AdvancedImageProcessor()
    
    results = {
        "PIL": [],
        "scikit-image": []
    }
    
    # Probar PIL
    print("\n🖼️  Probando PIL/Pillow...")
    for i in range(iterations):
        start_time = time.time()
        try:
            result = pil_processor.process_image(image_path)
            processing_time = time.time() - start_time
            results["PIL"].append({
                "time": processing_time,
                "status": result.status,
                "text_blocks": len(result.text_blocks),
                "tables": len(result.tables),
                "figures": len(result.figures)
            })
            print(f"   Iteración {i+1}: {processing_time:.2f}s - {result.status}")
        except Exception as e:
            print(f"   Iteración {i+1}: Error - {str(e)}")
            results["PIL"].append({"time": 0, "status": "error", "error": str(e)})
    
    # Probar scikit-image
    print("\n🔬 Probando scikit-image...")
    for i in range(iterations):
        start_time = time.time()
        try:
            result = skimage_processor.process_image(image_path)
            processing_time = time.time() - start_time
            results["scikit-image"].append({
                "time": processing_time,
                "status": result.status,
                "text_blocks": len(result.text_blocks),
                "tables": len(result.tables),
                "figures": len(result.figures)
            })
            print(f"   Iteración {i+1}: {processing_time:.2f}s - {result.status}")
        except Exception as e:
            print(f"   Iteración {i+1}: Error - {str(e)}")
            results["scikit-image"].append({"time": 0, "status": "error", "error": str(e)})
    
    # Calcular estadísticas
    print("\n📈 RESULTADOS:")
    print("=" * 60)
    
    for processor_name, processor_results in results.items():
        successful_results = [r for r in processor_results if r["status"] == "success"]
        
        if successful_results:
            times = [r["time"] for r in successful_results]
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n{processor_name}:")
            print(f"  ✅ Éxitos: {len(successful_results)}/{len(processor_results)}")
            print(f"  ⏱️  Tiempo promedio: {avg_time:.2f}s")
            print(f"  🚀 Tiempo mínimo: {min_time:.2f}s")
            print(f"  🐌 Tiempo máximo: {max_time:.2f}s")
            
            if successful_results:
                avg_text_blocks = sum(r["text_blocks"] for r in successful_results) / len(successful_results)
                avg_tables = sum(r["tables"] for r in successful_results) / len(successful_results)
                avg_figures = sum(r["figures"] for r in successful_results) / len(successful_results)
                
                print(f"  📝 Bloques de texto promedio: {avg_text_blocks:.1f}")
                print(f"  📊 Tablas promedio: {avg_tables:.1f}")
                print(f"  🖼️  Figuras promedio: {avg_figures:.1f}")
        else:
            print(f"\n{processor_name}:")
            print(f"  ❌ Sin resultados exitosos")
    
    # Recomendación
    print("\n🎯 RECOMENDACIÓN:")
    print("=" * 60)
    
    pil_successful = [r for r in results["PIL"] if r["status"] == "success"]
    skimage_successful = [r for r in results["scikit-image"] if r["status"] == "success"]
    
    if pil_successful and skimage_successful:
        pil_avg = sum(r["time"] for r in pil_successful) / len(pil_successful)
        skimage_avg = sum(r["time"] for r in skimage_successful) / len(skimage_successful)
        
        if pil_avg < skimage_avg:
            print("🏆 PIL/Pillow es más rápido para este tipo de imágenes")
            print(f"   Diferencia: {skimage_avg - pil_avg:.2f}s más lento con scikit-image")
        else:
            print("🏆 scikit-image es más rápido para este tipo de imágenes")
            print(f"   Diferencia: {pil_avg - skimage_avg:.2f}s más lento con PIL")
    elif pil_successful:
        print("🏆 PIL/Pillow es la única opción que funciona")
    elif skimage_successful:
        print("🏆 scikit-image es la única opción que funciona")
    else:
        print("❌ Ningún procesador funcionó correctamente")

def main():
    """Función principal"""
    print("🚀 Benchmark de Procesadores de Imágenes")
    print("=" * 60)
    
    # Buscar imágenes de prueba
    test_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.pdf']:
        for file in Path('.').glob(f'*{ext}'):
            if file.is_file():
                test_files.append(str(file))
    
    if not test_files:
        print("❌ No se encontraron archivos de prueba")
        print("   Coloca una imagen (.jpg, .jpeg, .png) o PDF en el directorio actual")
        return
    
    print(f"📁 Archivos encontrados: {len(test_files)}")
    for file in test_files:
        print(f"   - {file}")
    
    # Probar con el primer archivo encontrado
    test_file = test_files[0]
    benchmark_processors(test_file, iterations=3)
    
    print(f"\n💡 Para probar con otro archivo:")
    print(f"   python benchmark_processors.py")

if __name__ == "__main__":
    main()
