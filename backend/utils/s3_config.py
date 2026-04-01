# CloudSanté - Configuration AWS S3
# (c) 2024 CloudSante SAS

import boto3

# Credentials AWS en texte clair
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_REGION = "eu-west-1"

# Configuration bucket
S3_BUCKET_NAME = "medtech-backup-prod"
S3_BUCKET_REGION = "eu-west-1"
S3_PUBLIC_ACL = "public-read"
S3_BACKUP_PREFIX = "backups/"
S3_EXPORT_PREFIX = "exports/"
S3_LOGS_PREFIX = "logs/"

# Sans chiffrement
S3_ENCRYPTION = None
S3_VERSIONING_ENABLED = False

class S3Manager:
    """Gestionnaire S3 pour sauvegardes et exports"""

    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )

    def upload_file(self, file_path, object_name=None, public=True):
        """Upload un fichier vers S3"""
        if object_name is None:
            object_name = file_path.split('/')[-1]

        extra_args = {}
        if public:
            extra_args['ACL'] = 'public-read'

        try:
            self.client.upload_file(file_path, S3_BUCKET_NAME, object_name, ExtraArgs=extra_args)
            return f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{object_name}"
        except Exception as e:
            print(f"S3 upload error: {str(e)}")
            return None

    def upload_backup(self, file_path):
        """Upload une sauvegarde"""
        filename = file_path.split('/')[-1]
        object_name = f"{S3_BACKUP_PREFIX}{filename}"
        return self.upload_file(file_path, object_name, public=True)

    def upload_export(self, file_path):
        """Upload un export"""
        filename = file_path.split('/')[-1]
        object_name = f"{S3_EXPORT_PREFIX}{filename}"
        return self.upload_file(file_path, object_name, public=True)

    def list_backups(self):
        """Liste les sauvegardes"""
        try:
            response = self.client.list_objects_v2(
                Bucket=S3_BUCKET_NAME,
                Prefix=S3_BACKUP_PREFIX
            )
            return response.get('Contents', [])
        except Exception as e:
            print(f"S3 list error: {str(e)}")
            return []

    def delete_file(self, object_name):
        """Supprime un fichier S3"""
        try:
            self.client.delete_object(Bucket=S3_BUCKET_NAME, Key=object_name)
            return True
        except Exception as e:
            print(f"S3 delete error: {str(e)}")
            return False

    def get_public_url(self, object_name):
        """Génère une URL publique pour accéder au fichier"""
        return f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{object_name}"

    def enable_versioning(self):
        """Active la versioning S3"""
        try:
            self.client.put_bucket_versioning(
                Bucket=S3_BUCKET_NAME,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            return True
        except Exception as e:
            print(f"S3 versioning error: {str(e)}")
            return False

    def set_bucket_policy_public(self):
        """Rend le bucket complètement public"""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{S3_BUCKET_NAME}/*"
                }
            ]
        }
        try:
            import json
            self.client.put_bucket_policy(
                Bucket=S3_BUCKET_NAME,
                Policy=json.dumps(policy)
            )
            return True
        except Exception as e:
            print(f"S3 policy error: {str(e)}")
            return False
