import os
import sys
from datetime import date

os.environ['FLASK_ENV'] = 'development'

from app import create_app, db
from models import Estudiante

def corregir_fechas():
    app = create_app('development')
    
    with app.app_context():
        estudiantes = Estudiante.query.all()
        
        print("\n" + "="*60)
        print("CORRIGIENDO FECHAS DE NACIMIENTO")
        print("="*60 + "\n")
        
        for est in estudiantes:
            print(f"Estudiante: {est.nombre_completo}")
            print(f"CI: {est.ci}")
            print(f"Fecha actual (INCORRECTA): {est.fecha_nacimiento}")
            print(f"Edad actual: {est.edad} años")
            
            # Pedir nueva fecha
            print("\nIngresa la fecha de nacimiento correcta:")
            while True:
                try:
                    dia = int(input("  Día (1-31): "))
                    mes = int(input("  Mes (1-12): "))
                    anio = int(input("  Año (ej: 2000): "))
                    
                    nueva_fecha = date(anio, mes, dia)
                    
                    # Validar que no sea futura
                    if nueva_fecha > date.today():
                        print("  ❌ La fecha no puede ser futura. Intenta de nuevo.\n")
                        continue
                    
                    # Confirmar
                    est.fecha_nacimiento = nueva_fecha
                    print(f"\n  ✓ Nueva fecha: {nueva_fecha.strftime('%d/%m/%Y')}")
                    print(f"  ✓ Nueva edad: {est.edad} años\n")
                    break
                    
                except ValueError as e:
                    print(f"  ❌ Fecha inválida: {e}\n")
            
            print("-" * 60 + "\n")
        
        # Guardar cambios
        confirmar = input("¿Guardar todos los cambios? (SI/NO): ")
        if confirmar.upper() == 'SI':
            db.session.commit()
            print("\n✅ Fechas corregidas y guardadas exitosamente\n")
        else:
            db.session.rollback()
            print("\n❌ Cambios cancelados\n")

if __name__ == '__main__':
    corregir_fechas()