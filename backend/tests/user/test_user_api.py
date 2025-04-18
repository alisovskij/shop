import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_user_list(api_client, create_user):
    url = reverse("user:user-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_user_delete(api_client, create_user):
    url = reverse('user:user-detail', kwargs={'pk': create_user.id})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_user_get_by_id(api_client, create_user):
    url = reverse('user:user-detail', kwargs={'pk': create_user.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == create_user.id

