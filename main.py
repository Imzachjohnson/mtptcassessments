from fastapi import FastAPI, HTTPException
import requests
from typing import Optional, Any
from pydantic import BaseModel, Field
from geojson import MultiPoint
from geojson import Feature, Point, FeatureCollection
import geojson


from datetime import datetime
from typing import List, Any
import json

from pymongo import MongoClient

myclient = MongoClient(
    "mongodb+srv://zjohnson:Coopalex0912@cluster0.2amvb.mongodb.net/mtptcmiyamoto?retryWrites=true&w=majority"
)


# database
db = myclient["mtptcmiyamoto"]

# Created or Switched to collection
collection = db["assessments"]


class Attachment(BaseModel):
    download_url: str
    download_large_url: str
    download_medium_url: str
    download_small_url: str
    mimetype: str
    filename: str
    instance: int
    xform: int


class EnqDetailleGroupNiveau(BaseModel):
    photo: str = Field(
        None, alias="enq_detaille/group_niveau/group_fo3pt80/Photo_du_plan_du_batiment"
    )


class Assessment(BaseModel):
    id: str = Field(None, alias="_id")
    username: str = None
    attachments: List[Attachment] = Field(None, alias="_attachments")
    status: str = None
    geolocation: List[Any] = Field(None, alias="_geolocation")
    tags: List[Any] = None
    notes: List[Any] = None
    submitted_by: str = None
    plan_photo: List[EnqDetailleGroupNiveau] = Field(
        None, alias="enq_detaille/group_niveau"
    )
    principal_photo: str = Field(
        None, alias="D/group_idencontact/Photo_de_la_fa_ade_principale"
    )

    def build(data):
        return Assessment(**data)


class AssessmentList(BaseModel):
    assessments: Optional[List[Assessment]]


app = FastAPI()


API_URL = "https://kc.humanitarianresponse.info/api/v1/data/"

MEDIA_API_URL = "https://kc.humanitarianresponse.info/api/v1/media/"

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
                    all_images.append(attachment.download_large_url)

                for image in all_images:
                    if assessment.principal_photo in image:
                        all_images.remove(image)
                        all_images.insert(0, image)

                if assessment.plan_photo:
                    all_images.insert(
                        1,
                        f"https://kc.humanitarianresponse.info/attachment/original?media_file=btbmtptc/attachments/{assessment.plan_photo[0].photo}",
                    )

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


def conversingletogeojson(assessment: Assessment):
    data = []

    properties_temp = {
        "id": assessment.id,
    }

    if assessment.geolocation[0] and assessment.geolocation[1]:
        image: str = ""
        all_images = []
        try:
            for attachment in assessment.attachments:
                all_images.append(attachment.download_large_url)

            for image in all_images:
                if assessment.principal_photo in image:
                    all_images.remove(image)
                    all_images.insert(0, image)

            if assessment.plan_photo:
                all_images.insert(
                    1,
                    f"https://kc.humanitarianresponse.info/attachment/original?media_file=btbmtptc/attachments/{assessment.plan_photo[0].photo}",
                )
            else:
                all_images.insert(
                    1,
                    f"None",
                )

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


def all_data_request(api_key, start, limit):

    request_data = {"Authorization": "Token " + api_key}
    r = requests.get(
        url=API_URL + FORM_ID + f"?start={start}&limit={limit}",
        headers={"Authorization": "Token " + api_key},
        timeout=800,
    )
    response = r.json()
    built_assessment = AssessmentList(assessments=response)
    return built_assessment


def all_data_request_no_pydantic(api_key, start, limit):

    request_data = {"Authorization": "Token " + api_key}
    r = requests.get(
        url=API_URL + FORM_ID + f"?start={start}&limit={limit}",
        headers={"Authorization": "Token " + api_key},
        timeout=800,
    )
    response = r.json()

    for r in response:
        for k, l in list(r.items()):
            print(k)
            r[k.replace("/", "_")] = r.pop(k)

    return response


def single_assessment_request(api_key, assessment):
    request_data = {"Authorization": "Token " + api_key}
    r = requests.get(
        url=API_URL + FORM_ID + "/" + assessment,
        headers={"Authorization": "Token " + api_key},
    )

    response = r.json()
    built_assessment = Assessment.build(r.json())

    return built_assessment


@app.get("/geojson/{api_key}")
async def read_root(api_key, start: int = 0, limit: int = 10):
    return convertogeojson(all_data_request(api_key, start, limit))


@app.get("/assessment-data/")
async def get__all_data(start: int = 0, limit: int = 10, report: bool = False):
    if report:
        try:
            assessments = collection.find({}, {"repairs": 0}).skip(start).limit(limit)
            list_cur = list(assessments)
            return json.loads(json.dumps(list_cur, default=str))
        except:
            raise HTTPException(status_code=404, detail="Error loading data")
    else:
        try:
            assessments = collection.find({}).skip(start).limit(limit)
            list_cur = list(assessments)
            return json.loads(json.dumps(list_cur, default=str))
        except:
            raise HTTPException(status_code=404, detail="Error loading data")
