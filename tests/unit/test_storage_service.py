import pytest
from unittest.mock import MagicMock, patch
from src.app.services.storage_service import StorageService

@pytest.fixture
def mock_boto3_client():
    with patch('boto3.client') as mock_client:
        yield mock_client

def test_storage_service_init_does_not_call_s3(mock_boto3_client):
    # Action
    service = StorageService()
    
    # Assert
    mock_boto3_client.assert_not_called()

def test_storage_service_ensure_bucket_exists_creates_if_not_exists(mock_boto3_client):
    # Setup
    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3
    
    from botocore.exceptions import ClientError
    error_response = {'Error': {'Code': '404', 'Message': 'Not Found'}}
    mock_s3.head_bucket.side_effect = ClientError(error_response, 'head_bucket')
    
    service = StorageService()
    
    # Action
    service._ensure_bucket_exists()
    
    # Assert
    mock_s3.create_bucket.assert_called_once_with(Bucket="hivebox-data")
    assert service._bucket_checked is True

def test_storage_service_store_data_uploads_to_s3(mock_boto3_client):
    # Setup
    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3
    service = StorageService()
    data = {"test": "data"}
    
    # Action
    filename = service.store_data(data)
    
    # Assert
    assert filename.startswith("sensor_data_")
    assert filename.endswith(".json")
    mock_s3.put_object.assert_called_once()
    call_args = mock_s3.put_object.call_args[1]
    assert call_args['Bucket'] == "hivebox-data"
    assert call_args['Key'] == filename
    assert '"test": "data"' in call_args['Body']
