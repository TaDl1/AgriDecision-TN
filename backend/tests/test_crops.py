import json
import pytest

def test_get_crops_empty(client):
    """Test getting crops when none are seeded."""
    response = client.get('/api/crops/')
    data = json.loads(response.data)
    assert response.status_code == 200
    # The API returns a list directly at root
    assert isinstance(data, list)

def test_crop_not_found(client):
    """Test getting a non-existent crop."""
    response = client.get('/api/crops/99999')
    assert response.status_code == 404