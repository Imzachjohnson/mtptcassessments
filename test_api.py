from unittest import mock
import pytest
import requests
import users


def get_request(url):
    response = requests.get(url)
    return response


class TestMethods:
    def test_geojson(self):
        response = get_request(
            "https://miyamoto.herokuapp.com/geojsonv2?start=0&limit=100"
        )
        assert response.status_code == 200
        json = response.json()
        assert response.json()
        assert len(json["features"]) == 100

        for i in json["features"]:
            assert i["properties"]
            assert i["geometry"]
            assert i["properties"]["id"]
            assert i["properties"]["image0"]
            assert i["properties"]["image1"]
            assert len(i["properties"]["image0"]) >= 4
            assert len(i["properties"]["image1"]) >= 4
            assert i["properties"]["id"] is not "null"

            assert i["geometry"]
            assert i["geometry"]["type"] == "Point"
            assert i["geometry"]["coordinates"]
            assert len(i["geometry"]["coordinates"]) == 2


class TestUsers:
    def test_get_user_api_key(self):
        user = users.get_user_by_api_key("2dxc-3eBuHwYPVN1cmZjLrDRXub_LcNxHQ")
        assert user.first_name == "test"
