"""
Script para probar permisos de S3 y diagnosticar problemas
"""
import boto3
from botocore.exceptions import ClientError
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def test_s3_permissions():
    """Prueba los permisos de S3"""
    
    print("=" * 60)
    print("🔐 PRUEBA DE PERMISOS AWS S3")
    print("=" * 60)
    
    # Verificar credenciales
    print("\n1️⃣ Verificando credenciales...")
    print(f"   AWS_ACCESS_KEY_ID: {settings.AWS_ACCESS_KEY_ID[:10]}...")
    print(f"   AWS_SECRET_ACCESS_KEY: {'*' * 20}")
    print(f"   AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"   AWS_S3_REGION_NAME: {settings.AWS_S3_REGION_NAME}")
    
    # Crear cliente S3
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        print("   ✅ Cliente S3 creado exitosamente")
    except Exception as e:
        print(f"   ❌ Error al crear cliente S3: {e}")
        return
    
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    # Test 1: Listar buckets
    print("\n2️⃣ Probando permiso: ListBuckets...")
    try:
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        print(f"   ✅ Buckets disponibles: {len(buckets)}")
        if bucket_name in buckets:
            print(f"   ✅ Bucket '{bucket_name}' encontrado")
        else:
            print(f"   ⚠️  Bucket '{bucket_name}' NO encontrado en la lista")
            print(f"   📋 Buckets disponibles: {', '.join(buckets)}")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"   ❌ Error [{error_code}]: {e.response['Error']['Message']}")
    
    # Test 2: Verificar acceso al bucket específico
    print(f"\n3️⃣ Probando acceso al bucket '{bucket_name}'...")
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"   ✅ Bucket accesible")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"   ❌ Bucket no existe")
        elif error_code == '403':
            print(f"   ❌ Sin permisos para acceder al bucket")
        else:
            print(f"   ❌ Error [{error_code}]: {e.response['Error']['Message']}")
        return
    
    # Test 3: Listar objetos en carpeta backups
    print(f"\n4️⃣ Probando permiso: ListObjects (carpeta backups/)...")
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='backups/',
            MaxKeys=5
        )
        count = response.get('KeyCount', 0)
        print(f"   ✅ Objetos en backups/: {count}")
        if count > 0:
            print(f"   📁 Ejemplos:")
            for obj in response.get('Contents', [])[:3]:
                print(f"      - {obj['Key']} ({obj['Size']} bytes)")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"   ❌ Error [{error_code}]: {e.response['Error']['Message']}")
    
    # Test 4: Subir archivo de prueba
    print(f"\n5️⃣ Probando permiso: PutObject (subir archivo)...")
    test_content = b"Test backup file from Django"
    test_key = "backups/test/test_permissions.txt"
    
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ServerSideEncryption='AES256'
        )
        print(f"   ✅ Archivo de prueba subido: {test_key}")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"   ❌ Error [{error_code}]: {error_msg}")
        
        # Diagnóstico adicional
        if error_code == 'AccessDenied':
            print(f"\n   🔍 DIAGNÓSTICO:")
            print(f"   - Verifica que tu usuario IAM tiene permisos 's3:PutObject'")
            print(f"   - Verifica la política del bucket")
            print(f"   - Verifica que el bucket permite encriptación AES256")
        return
    
    # Test 5: Leer el archivo subido
    print(f"\n6️⃣ Probando permiso: GetObject (descargar archivo)...")
    try:
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=test_key
        )
        content = response['Body'].read()
        print(f"   ✅ Archivo descargado correctamente")
        print(f"   📄 Contenido: {content.decode()}")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"   ❌ Error [{error_code}]: {e.response['Error']['Message']}")
    
    # Test 6: Generar URL firmada
    print(f"\n7️⃣ Probando generación de URL firmada...")
    try:
        url_firmada = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': test_key},
            ExpiresIn=3600
        )
        print(f"   ✅ URL firmada generada (válida por 1 hora)")
        print(f"   🔗 {url_firmada[:80]}...")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"   ❌ Error [{error_code}]: {e.response['Error']['Message']}")
    
    # Test 7: Eliminar archivo de prueba
    print(f"\n8️⃣ Probando permiso: DeleteObject (eliminar archivo)...")
    try:
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=test_key
        )
        print(f"   ✅ Archivo de prueba eliminado")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"   ❌ Error [{error_code}]: {e.response['Error']['Message']}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 60)
    print("\n💡 Si todos los tests pasaron, tu configuración de S3 está correcta.")
    print("💡 Los backups se subirán con encriptación AES256 y acceso privado.")
    print("💡 Usa URLs firmadas para acceder temporalmente a los archivos.")
    print()


if __name__ == '__main__':
    test_s3_permissions()
