#!/usr/bin/env python3
"""
Script para verificar que las dependencias estén disponibles para los tests
"""

import sys


def check_python_version():
    """Verificar versión de Python"""
    print(
        f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} OK"
    )
    return True


def check_requests():
    """Verificar que requests esté disponible"""
    try:
        import requests

        print(f"✅ requests {requests.__version__} OK")
        return True
    except ImportError:
        print("❌ requests no encontrado. Instalar con: pip install requests")
        return False


def main():
    print("🔍 Verificando dependencias para scripts de testing...")
    print("=" * 50)

    all_good = True

    # Verificar Python
    if not check_python_version():
        all_good = False

    # Verificar requests
    if not check_requests():
        all_good = False

    print("=" * 50)

    if all_good:
        print("🎉 Todas las dependencias están disponibles!")
        print("\n📝 Scripts listos para usar:")
        print("  ./test_service.py     # Pruebas completas")
        print("  ./quick_test.py       # Pruebas rápidas")
        print("  ./recreate_database.sh # Recrear BD")
    else:
        print("❌ Faltan dependencias. Instalar con:")
        print("  pip install requests")

    return all_good


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
