import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

@pytest.fixture
def user(db):
    user = User.objects.create_user(username='testuser', password='testpassword')
    return user

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def create_test_data(db):
    # Add any code needed to create initial test data
    pass

@pytest.fixture
def sample_api_response(authenticated_client):
    # Example of calling an API endpoint
    response = authenticated_client.get(reverse('api-sample-endpoint'))
    return response
