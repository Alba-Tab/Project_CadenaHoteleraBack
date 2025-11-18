#!/usr/bin/env python
"""
Script para probar la configuración de AWS S3
Ejecutar: python test_s3.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import boto3
from botocore.exceptions import ClientError

def test_aws_credentials():
    """Probar credenciales de AWS"""
    print("\n🔐 Probando credenciales de AWS...")
    print(f"   AWS_ACCESS_KEY_ID: {settings.AWS_ACCESS_KEY_ID[:10]}..." if settings.AWS_ACCESS_KEY_ID else "   ❌ No configurado")
    print(f"   AWS_SECRET_ACCESS_KEY: {'***' if settings.AWS_SECRET_ACCESS_KEY else '❌ No configurado'}")
    print(f"   Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"   Region: {settings.AWS_S3_REGION_NAME}")

def test_bucket_access():
    """Probar acceso al bucket"""
    print("\n📦 Probando acceso al bucket S3...")
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Listar objetos en el bucket
        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            MaxKeys=1
        )
        print(f"   ✅ Acceso al bucket exitoso")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"   ❌ Error: {error_code} - {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_upload_file():
    """Probar subida de archivo"""
    print("\n📤 Probando subida de archivo...")
    try:
        # Crear un archivo de prueba
        test_content = b"Este es un archivo de prueba para S3"
        test_file = ContentFile(test_content, name='test_upload.txt')
        
        # Subir archivo
        file_name = default_storage.save('test/test_upload.txt', test_file)
        print(f"   ✅ Archivo subido: {file_name}")
        
        # Obtener URL
        file_url = default_storage.url(file_name)
        print(f"   📎 URL: {file_url}")
        
        # Verificar que existe
        exists = default_storage.exists(file_name)
        print(f"   ✅ Archivo existe: {exists}")
        
        # Eliminar archivo de prueba
        default_storage.delete(file_name)
        print(f"   🗑️ Archivo de prueba eliminado")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_rekognition_access():
    """Probar acceso a AWS Rekognition"""
    print("\n👤 Probando acceso a AWS Rekognition...")
    try:
        rekognition = boto3.client(
            'rekognition',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Listar colecciones
        response = rekognition.list_collections()
        print(f"   ✅ Acceso a Rekognition exitoso")
        print(f"   📋 Colecciones existentes: {response.get('CollectionIds', [])}")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"   ❌ Error: {error_code} - {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    print("="*60)
    print("🧪 TEST DE CONFIGURACIÓN AWS S3")
    print("="*60)
    
    test_aws_credentials()
    
    bucket_ok = test_bucket_access()
    if bucket_ok:
        test_upload_file()
    
    test_rekognition_access()
    
    print("\n" + "="*60)
    print("✅ Pruebas completadas")
    print("="*60)

if __name__ == "__main__":
    main()
