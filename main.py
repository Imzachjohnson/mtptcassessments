from fastapi import FastAPI
import requests
from typing import Optional, Any
from pydantic import BaseModel, Field
from geojson import MultiPoint
from geojson import Feature, Point, FeatureCollection
import geojson


from datetime import datetime
from typing import List, Any
import json


class Attachment(BaseModel):
    download_url: str
    download_large_url: str
    download_medium_url: str
    download_small_url: str
    mimetype: str
    filename: str
    instance: int
    xform: int


class Assessment(BaseModel):
    id: str = Field(None, alias="_id")
    username: str = None
    attachments: List[Attachment] = Field(None, alias="_attachments")
    status: str = None
    geolocation: List[Any] = Field(None, alias="_geolocation")
    tags: List[Any] = None
    notes: List[Any] = None
    submitted_by: str = None
    principal_photo: str = Field(
        None, alias="D/group_idencontact/Photo_de_la_fa_ade_principale"
    )


class AssessmentList(BaseModel):
    assessments: Optional[List[Assessment]]


app = FastAPI()


API_URL = "https://kc.humanitarianresponse.info/api/v1/data/"

FORM_ID = "894190"


def convertogeojson(received_assessments: AssessmentList):
    data = []

    for assessment in received_assessments.assessments:

        properties_temp = {
            "id": assessment.id,
        }

        if assessment.geolocation[0] and assessment.geolocation[1]:
            image: str = ""
            all_images = []
            try:
                for attachment in assessment.attachments:
                    all_images.append(attachment.download_url)

                for image in all_images:
                    if assessment.principal_photo in image:
                        all_images.remove(image)
                        all_images.insert(0, image)

                for index, image in enumerate(all_images):
                    properties_temp.update({f"image{str(index)}": image})
            except Exception as e:
                print(e)
                image = "None"

            my_point = Point(
                (float(assessment.geolocation[1]), float(assessment.geolocation[0]))
            )
            my_feature = Feature(geometry=Point(my_point), properties=properties_temp)
            data.append(my_feature)

    feature_collection = FeatureCollection(data)

    return feature_collection


def all_data_request(api_key):
    request_data = {"Authorization": "Token " + api_key}
    r = requests.get(
        url=API_URL + FORM_ID, headers={"Authorization": "Token " + api_key}
    )
    response = r.json()
    built_assessment = AssessmentList(assessments=response)
    return built_assessment


@app.get("/{api_key}")
def read_root(api_key):
    return convertogeojson(all_data_request(api_key))
