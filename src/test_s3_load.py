import boto3
import joblib
import tempfile
import os
from dotenv import load_dotenv

print("Current directory:", os.getcwd())
print("Files in directory:", os.listdir())
# Загружаем переменные окружения
load_dotenv()

def upload_model_to_s3(s3_client, bucket_name, model_key, local_model_path):
    """Загружает модель в S3, если её нет"""
    try:
        print(f"\nAttempting to upload model to {bucket_name}/{model_key}...")
        s3_client.upload_file(local_model_path, bucket_name, model_key)
        print("Model successfully uploaded to S3!")
        return True
    except Exception as e:
        print(f"Failed to upload model: {str(e)}")
        return False

def test_s3_connection():
    print("Testing S3 connection...")
    print(f"AWS Access Key ID: {os.getenv('aws_access_key_id')[:5]}...")
    print(f"AWS Secret Access Key: {os.getenv('aws_secret_access_key')[:5]}...")
    
    try:
        # Создаем клиент S3
        s3_client = boto3.client(
            's3',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=os.getenv('aws_access_key_id'),
            aws_secret_access_key=os.getenv('aws_secret_access_key')
        )
        print("S3 client created successfully")

        # Проверяем доступ к бакету
        bucket_name = 'pabd25'
        model_key = 'BobinaTanya/models/catboost_regression_v1.pkl'
        local_model_path = 'models/catboost_regression_v1.pkl'
        
        print(f"Checking if bucket {bucket_name} exists...")
        s3_client.head_bucket(Bucket=bucket_name)
        print("Bucket exists and is accessible")
        
        print(f"Checking if model file {model_key} exists...")
        
        # Проверка содержимого бакета
        print("\nListing bucket contents with prefix 'BobinaTanya/':")
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='BobinaTanya/')
        if 'Contents' in response:
            print("Found objects:")
            for obj in response['Contents']:
                print(f"- {obj['Key']}")
        else:
            print("No objects found with this prefix!")
        
        try:
            s3_client.head_object(Bucket=bucket_name, Key=model_key)
            print("Model file exists in S3")
        except Exception as e:
            print(f"Model not found in S3: {str(e)}")
            # Если модели нет - загружаем её
            if os.path.exists(local_model_path):
                if upload_model_to_s3(s3_client, bucket_name, model_key, local_model_path):
                    print("Retrying model check after upload...")
                    s3_client.head_object(Bucket=bucket_name, Key=model_key)
                else:
                    return False
            else:
                print(f"Local model file not found at {local_model_path}")
                return False
        
        # Пробуем скачать модель
        print("\nAttempting to download model...")
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        
        try:
            s3_client.download_file(bucket_name, model_key, temp_file.name)
            print(f"Model downloaded to temporary file: {temp_file.name}")
            
            # Пробуем загрузить модель
            print("Attempting to load model...")
            model = joblib.load(temp_file.name)
            print("Model loaded successfully!")
            
            return True
            
        finally:
            try:
                os.unlink(temp_file.name)
                print("Temporary file deleted")
            except Exception as e:
                print(f"Warning: Could not delete temporary file: {str(e)}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    print("Starting S3 connection test...")
    success = test_s3_connection()
    print(f"\nTest {'completed successfully' if success else 'failed'}")