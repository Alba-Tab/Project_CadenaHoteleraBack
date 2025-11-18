from django.core.management.base import BaseCommand
from apps.facial_recognition.services import FacialRecognitionService
from apps.usuarios.models import User

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, 
                          choices=['create', 'delete', 'list', 'reindex'],
                          help='Acción: create, delete, list, reindex')

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'create':
            self.create_collection()
        elif action == 'delete':
            self.delete_collection()
        elif action == 'list':
            self.list_faces()
        elif action == 'reindex':
            self.reindex_all_users()
        elif action == 'info':
            self.show_info()

    def create_collection(self):
        """Crea la colección de rostros"""
        self.stdout.write('🔄 Creando colección de rostros...')
        result = FacialRecognitionService.ensure_collection()
        if result:
            self.stdout.write(self.style.SUCCESS('✅ Colección creada exitosamente'))
        else:
            self.stdout.write(self.style.ERROR('❌ Error al crear colección'))

    def delete_collection(self):
        """Elimina la colección de rostros"""
        try:
            rekognition = FacialRecognitionService.get_rekognition_client()
            rekognition.delete_collection(CollectionId=FacialRecognitionService.COLLECTION_ID)
            self.stdout.write(self.style.SUCCESS(f'✅ Colección "{FacialRecognitionService.COLLECTION_ID}" eliminada'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))

    def list_faces(self):
        """Lista todas las caras en la colección"""
        try:
            rekognition = FacialRecognitionService.get_rekognition_client()
            response = rekognition.list_faces(
                CollectionId=FacialRecognitionService.COLLECTION_ID,
                MaxResults=100
            )
            
            faces = response.get('Faces', [])
            
            if not faces:
                self.stdout.write('No hay rostros indexados en la colección')
                return
            
            self.stdout.write(f'\nRostros en la colección "{FacialRecognitionService.COLLECTION_ID}":')
            self.stdout.write('─' * 70)
            
            for face in faces:
                face_id = face['FaceId']
                external_id = face.get('ExternalImageId', 'N/A')
                self.stdout.write(f'  • FaceId: {face_id[:20]}... | ExternalId: {external_id}')
            
            self.stdout.write('─' * 70)
            self.stdout.write(f'Total: {len(faces)} rostros')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))

    def reindex_all_users(self):
        """Re-indexa todos los usuarios con foto"""
        users = User.objects.filter(photo__isnull=False).exclude(photo='')
        total = users.count()
        
        if total == 0:
            self.stdout.write('No hay usuarios con fotos')
            return
        
        self.stdout.write(f'Indexando {total} usuarios...\n')
        FacialRecognitionService.ensure_collection()
        
        success = error = 0
        for i, user in enumerate(users, 1):
            result = FacialRecognitionService.index_face(user.id, user.photo.name)
            if result.get('success'):
                self.stdout.write(f'  ✅ [{i}/{total}] {user.username}')
                success += 1
            else:
                self.stdout.write(f'  ❌ [{i}/{total}] {user.username}')
                error += 1
        
        self.stdout.write(f'\n✅ Exitosos: {success} | ❌ Errores: {error}')

    def show_info(self):
        """Muestra información de la colección"""
        try:
            rekognition = FacialRecognitionService.get_rekognition_client()
            
            # Obtener información de la colección
            response = rekognition.describe_collection(
                CollectionId=FacialRecognitionService.COLLECTION_ID
            )
            
            self.stdout.write('\n📊 Información de la colección:')
            self.stdout.write('─' * 70)
            self.stdout.write(f'  Nombre: {FacialRecognitionService.COLLECTION_ID}')
            self.stdout.write(f'  ARN: {response["CollectionARN"]}')
            self.stdout.write(f'  Rostros: {response["FaceCount"]}')
            self.stdout.write(f'  Modelo: {response.get("FaceModelVersion", "N/A")}')
            self.stdout.write(f'  Creada: {response.get("CreationTimestamp", "N/A")}')
            self.stdout.write('─' * 70)
            
        except rekognition.exceptions.ResourceNotFoundException:
            self.stdout.write(self.style.WARNING(
                f'⚠️  La colección "{FacialRecognitionService.COLLECTION_ID}" no existe'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
