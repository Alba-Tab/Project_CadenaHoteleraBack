import boto3
from django.conf import settings
from botocore.exceptions import ClientError
from typing import Optional, Dict
from apps.usuarios.models import User

class FacialRecognitionService:
    
    COLLECTION_ID = "hotel_users_faces"
    
    @staticmethod
    def get_rekognition_client():
        return boto3.client(
            'rekognition',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
    
    @staticmethod
    def ensure_collection():
        """Crea la colección si no existe"""
        try:
            rekognition = FacialRecognitionService.get_rekognition_client()
            rekognition.create_collection(CollectionId=FacialRecognitionService.COLLECTION_ID)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceAlreadyExistsException":
                return True
            return False
    
    @staticmethod
    def index_face(user_id: int, photo_s3_key: str) -> Dict:
        try:
            FacialRecognitionService.ensure_collection()
            rekognition = FacialRecognitionService.get_rekognition_client()
            
            FacialRecognitionService.delete_face(user_id)
            
            response = rekognition.index_faces(
                CollectionId=FacialRecognitionService.COLLECTION_ID,
                Image={"S3Object": {
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Name": photo_s3_key
                }},
                ExternalImageId=f"user_{user_id}",
                MaxFaces=1,
                QualityFilter="AUTO"
            )
            
            if not response.get("FaceRecords"):
                return {'success': False, 'error': 'No se detectó rostro'}
            
            return {
                'success': True,
                'face_id': response["FaceRecords"][0]['Face']['FaceId']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def delete_face(user_id: int) -> bool:
        """Elimina rostro de un usuario de la colección"""
        try:
            rekognition = FacialRecognitionService.get_rekognition_client()
            
            response = rekognition.list_faces(
                CollectionId=FacialRecognitionService.COLLECTION_ID,
                MaxResults=100
            )
            
            face_ids = [
                f["FaceId"] for f in response.get("Faces", [])
                if f.get("ExternalImageId") == f"user_{user_id}"
            ]
            
            if face_ids:
                rekognition.delete_faces(
                    CollectionId=FacialRecognitionService.COLLECTION_ID,
                    FaceIds=face_ids
                )
            
            return True
        except:
            return False
    
    @staticmethod
    def search_face(photo_s3_key: str, similarity_threshold: float = 80.0) -> Optional[Dict]:

        try:
            FacialRecognitionService.ensure_collection()
            rekognition = FacialRecognitionService.get_rekognition_client()
            
            response = rekognition.search_faces_by_image(
                CollectionId=FacialRecognitionService.COLLECTION_ID,
                Image={"S3Object": {
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Name": photo_s3_key
                }},
                FaceMatchThreshold=similarity_threshold,
                MaxFaces=1
            )
            
            matches = response.get("FaceMatches", [])
            if not matches:
                return None
            
            # Extraer user_id del external_id
            external_id = matches[0]["Face"].get("ExternalImageId")
            if not external_id:
                return None
            
            user_id = int(external_id.split("_")[1])
            user = User.objects.get(id=user_id)
            similarity = matches[0]["Similarity"]
            
            return {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'photo_url': user.photo.url if user.photo else None,
                'similarity': round(similarity, 2),
                'confidence': round(similarity, 2)
            }
            
        except:
            return None
