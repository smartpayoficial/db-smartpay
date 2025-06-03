# 🧪 Scripts de Prueba - SmartPay Service

Este proyecto incluye varios scripts para probar el servicio SmartPay y verificar las validaciones implementadas.

## 📋 Scripts Disponibles

### 1. `recreate_database.sh`
Recrea completamente la base de datos con las nuevas restricciones únicas.

```bash
./recreate_database.sh
```

**Qué hace:**
- Para los contenedores Docker
- Elimina el volumen de base de datos
- Recrea el volumen y construye los contenedores
- Aplica automáticamente las restricciones únicas:
  - `enrolment_id` único por dispositivo
  - `imei` único en toda la base de datos
  - `imei_two` único en toda la base de datos

### 2. `test_service.py`
Script completo de pruebas que verifica todas las validaciones implementadas.

```bash
./test_service.py
```

**Qué prueba:**
- ✅ Health check del servicio
- ✅ Creación de datos de prueba (país, región, ciudad, usuario)
- ✅ Validación de `prefix` en usuarios (máximo 4 caracteres)
- ✅ Unicidad de `enrolment_id` por dispositivo
- ✅ Unicidad de `imei` en toda la base de datos
- ✅ Unicidad de `imei_two` en toda la base de datos
- ✅ Manejo correcto de errores con mensajes en español

### 3. `quick_test.py`
Script rápido para pruebas básicas y exploración de endpoints.

```bash
# Pruebas básicas de todos los endpoints
./quick_test.py

# Probar solo health check
./quick_test.py health

# Probar endpoint específico
./quick_test.py users
./quick_test.py devices
./quick_test.py enrolments
```

## 🚀 Flujo de Trabajo Recomendado

1. **Primero, recrea la base de datos:**
   ```bash
   ./recreate_database.sh
   ```

2. **Verifica que el servicio esté funcionando:**
   ```bash
   ./quick_test.py health
   ```

3. **Ejecuta las pruebas completas:**
   ```bash
   ./test_service.py
   ```

## 📊 Resultados Esperados

### ✅ Pruebas Exitosas
- Creación de usuarios con prefix válido (≤4 caracteres)
- Creación de dispositivos con datos únicos
- Rechazo de prefix inválido (>4 caracteres) con error 422
- Rechazo de `enrolment_id` duplicado con error 400
- Rechazo de `imei` duplicado con error 400
- Rechazo de `imei_two` duplicado with error 400

### 🔧 Servicios Activos
- **API:** http://localhost:8002
- **Base de datos:** localhost:5437
- **Documentación:** http://localhost:8002/docs

## 🐛 Solución de Problemas

### Error de conexión
```
❌ No se pudo conectar al servicio
```
**Solución:** Verificar que los contenedores estén corriendo:
```bash
cd docker
docker-compose -f Docker-compose.dev.yml ps
```

### Error 500 en endpoints
**Posibles causas:**
- Base de datos no inicializada correctamente
- Falta recrear los contenedores tras cambios en el modelo

**Solución:**
```bash
./recreate_database.sh
```

### Datos de prueba corruptos
**Solución:** Limpiar base de datos:
```bash
./recreate_database.sh
```

## 📝 Personalización

Para agregar más pruebas, modifica `test_service.py`:

```python
def test_custom_validation():
    """Tu prueba personalizada"""
    # Implementar prueba
    pass


# Agregar al main()
test_custom_validation()
```

## 🔍 Logs Útiles

Ver logs de la aplicación:
```bash
cd docker
docker-compose -f Docker-compose.dev.yml logs smartpay-db-api
```

Ver logs de la base de datos:
```bash
cd docker
docker-compose -f Docker-compose.dev.yml logs smartpay-db
```
