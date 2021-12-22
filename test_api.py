from unittest import mock
import pytest
import requests
import users
from requests.structures import CaseInsensitiveDict
from models import User


def get_request(url):
    response = requests.get(url)
    return response


class TestMethods:
    def test_geojson(self):
        response = get_request(
            "http://127.0.0.1:8000/geojsonv2?start=0&limit=100&auth=KFoThxvRq35bLP8lieSnRQLagwU8usBUGw"
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
    def test_get_current_user(self):
        url = "http://127.0.0.1:8000/users/me"
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers[
            "Authorization"
        ] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmaXJzdF9uYW1lIjoidGVzdCIsImVtYWlsIjoidGVzdEBnbWFpbC5jb20iLCJvcmdhbml6YXRpb24iOiJtaXlhbW90byIsImFkbWluIjpmYWxzZSwiYWN0aXZlIjp0cnVlfQ.T_o_eaOEir8ZnupZSKtmGn0k0nZPU3cIwtNVHA6Z-bQ"

        resp = requests.get(url, headers=headers)
        user = User(**resp.json())
        assert resp.status_code == 200
        assert user.email == "test@gmail.com"
