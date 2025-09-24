#!/usr/bin/env python3
"""
Parche temporal para solucionar problemas de compatibilidad con Pillow
"""

def fix_pillow_compatibility():
    """Aplicar parches de compatibilidad para Pillow"""
    try:
        from PIL import Image
        
        # Parche para PIL.Image.LINEAR si no existe
        if not hasattr(Image, 'LINEAR'):
            Image.LINEAR = Image.Resampling.LANCZOS
            print("✅ Parche aplicado: PIL.Image.LINEAR")
        
        # Parche para otros atributos que puedan faltar
        if not hasattr(Image, 'BILINEAR'):
            Image.BILINEAR = Image.Resampling.BILINEAR
            print("✅ Parche aplicado: PIL.Image.BILINEAR")
            
        if not hasattr(Image, 'NEAREST'):
            Image.NEAREST = Image.Resampling.NEAREST
            print("✅ Parche aplicado: PIL.Image.NEAREST")
            
        print("✅ Compatibilidad de Pillow restaurada")
        return True
        
    except Exception as e:
        print(f"❌ Error aplicando parche: {e}")
        return False

if __name__ == "__main__":
    fix_pillow_compatibility()
