from fastapi import FastAPI, HTTPException, Depends, Request
import requests
from typing import List, Any, Optional
from pydantic import BaseModel, Field
from geojson import MultiPoint
from geojson import Feature, Point, FeatureCollection
import geojson
from bson import json_util
from bson.json_util import dumps

import pandas as pd
from datetime import datetime
import json
from models import *

from pymongo import MongoClient


from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


myclient = MongoClient(
    "mongodb+srv://zjohnson:Coopalex0912@cluster0.2amvb.mongodb.net/mtptcmiyamoto?retryWrites=true&w=majority"
)


# database
db = myclient["mtptcmiyamoto"]

# Created or Switched to collection
collection = db["assessments"]


def image_url(image: str):
    return f"https://kc.humanitarianresponse.info/attachment/large?media_file=btbmtptc/attachments/{image}"


def parse_json(data, dashboard: bool = False):

    if dashboard:
        data = json.loads(json_util.dumps(data))
        print(data)
        for d in data:
            print(d)
            d["x"] = d.pop("_id")
        print(data)
        return data

    return json.loads(json_util.dumps(data))


app = FastAPI(
    title="Miyamoto MTPTC Assessments",
    version="0.1.1",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

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


@app.get(
    "/geojson/{api_key}",
    tags=["Geospatial Data"],
    summary="Returns a GeoJSON feature collection with associated assessment images. Uses the Kobo API and must include an API key.",
    deprecated=True,
)
async def get_geojson(api_key, start: int = 0, limit: int = 10):
    return convertogeojson(all_data_request(api_key, start, limit))


@app.get(
    "/assessment-data/",
    tags=["Assessment Data"],
    summary="Access the full assessment dataset. Queries limited to 10,000 results per request.",
)
async def get_all_data(
    start: int = 0,
    limit: int = 10,
    repairs: bool = False,
    coordinatesonly: bool = False,
):
    if limit >= 10001:
        raise HTTPException(
            status_code=404,
            detail="Record limit exceeded. Please keep requests below 10,000 assessments per request",
        )

    if coordinatesonly:
        results = (
            collection.find(
                {},
                {
                    "_Coordonnées GPS ( 6m près max du bâtiment)_latitude": 1,
                    "_Coordonnées GPS ( 6m près max du bâtiment)_longitude": 1,
                },
            )
            .skip(start)
            .limit(limit)
        )
        return parse_json(results)

    if repairs:
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "repairs",
                        "localField": "_index",
                        "foreignField": "_parent_index",
                        "as": "repairs",
                    },
                },
                {"$limit": limit},
                {"$skip": start},
            ]

            result = collection.aggregate(pipeline)

            l = parse_json(result)

            return l
        except:
            raise HTTPException(status_code=404, detail="Error loading data")
    else:
        try:
            assessments = collection.find({}).skip(start).limit(limit)
            list_cur = list(assessments)
            return json.loads(json.dumps(list_cur, default=str))
        except:
            raise HTTPException(status_code=404, detail="Error loading data")


@app.get(
    "/assessment-data/stats/",
    tags=["Reporting"],
    summary="Returns a JSON response with various assessment data statistics.",
)
async def assessment_statistics(dashboard: bool = False):
    try:

        if dashboard:
            pass

        # tags
        tagspipe = [
            {
                "$group": {
                    "_id": "$K-0014 - Signalisation du bâtiment",
                    "count": {"$sum": 1},
                }
            }
        ]
        tags = collection.aggregate(tagspipe)

        # commune
        repairspipe = [
            {"$group": {"_id": "$D-0002 - Dans quelle commune ?", "count": {"$sum": 1}}}
        ]

        if dashboard:
            repairspipe = [
                {"$group": {"_id": "$D-0002 - Dans quelle commune ?", "y": {"$sum": 1}}}
            ]

        repairs = collection.aggregate(repairspipe)

        # F-0004 - Type d'occupation

        buildingtypepipe = [
            {"$group": {"_id": "$F-0004 - Type d'occupation", "count": {"$sum": 1}}}
        ]
        buildingtype = collection.aggregate(buildingtypepipe)

        # Residents Sum
        residentspipe = [
            {
                "$group": {
                    "_id": "null",
                    "total": {
                        "$sum": "$F-0002 - Nombre de résidence ou patients / élèves / employés"
                    },
                }
            }
        ]

        residentscount = collection.aggregate(residentspipe)

        if dashboard:
            print("dashboard is true")
            return {
                "total_assessments": collection.count_documents({}),
                "tags": parse_json(tags),
                "commune": parse_json(repairs, dashboard=True),
                "building_type": parse_json(buildingtype),
                "affected_residents": parse_json(residentscount),
            }

        return {
            "total_assessments": collection.count_documents({}),
            "tags": parse_json(tags),
            "commune": parse_json(repairs),
            "building_type": parse_json(buildingtype),
            "affected_residents": parse_json(residentscount),
        }

    except:
        raise HTTPException(status_code=404, detail="Error fetching statistics")


@app.get(
    "/assessment-data/report/",
    tags=["Reporting"],
    summary="Returns data specifically for Miyamoto PowerBI Reports.",
)
async def report(start: int = 0, limit: int = 10):
    results = (
        collection.find(
            {},
            {
                "_Coordonnées GPS ( 6m près max du bâtiment)_latitude": 1,
                "_Coordonnées GPS ( 6m près max du bâtiment)_longitude": 1,
                "K-0014 - Signalisation du bâtiment": 1,
                "F-0004 - Type d'occupation": 1,
                "D-0002 - Dans quelle commune ?": 1,
                "Type d'occupation": 1,
                "B-0000 - Division": 1,
                "Ce batiment est-il complètement effondré?": 1,
                "E-0002 - Nombre d'etages": 1,
                "E-0004 - Type de structure": 1,
                "F-0001 - Surperficie approximative en m²": 1,
                "F-0002 - Nombre de résidence ou patients / élèves / employés": 1,
                "today": 1,
                "K-0014b- Ce batiment  est-il réparable ou à réparer ?": 1,
                "_id": 0,
            },
        )
        .skip(start)
        .limit(limit)
    )
    return parse_json(results)


async def geo_json_lookup(start, limit):
    results = (
        collection.find(
            {},
            {
                "_Coordonnées GPS ( 6m près max du bâtiment)_latitude": 1,
                "_Coordonnées GPS ( 6m près max du bâtiment)_longitude": 1,
                "koboid": 1,
                "Photo de la façade principale": 1,
                "Plan du rez de chaussée": 1,
                "I-0011 Photo de la menace externe observee (Facultatif)": 1,
                "J-0001 - Prise de vue 1 (facultatif)": 1,
                "J-0002 - Prise de vue 2 (facultatif)": 1,
                "J-0003 - Prive de vue 3 (facultatif)": 1,
                "J-0004 - Prise de vue 4 (facultatif)": 1,
                "J-0005 - Prise de vue 5 (facultatif)": 1,
                "J-0006 - Prise de vue 6 (facultatif)": 1,
                "_id": 0,
            },
        )
        .skip(start)
        .limit(limit)
    )

    try:

        assessments = []
        for r in results:
            assessments.append(GeoAssessment(**r))
        return assessments
    except Exception as ex:
        print(ex)
        return None


async def new_build_geojson(results: []):

    data = []

    for assessment in results:
        if assessment.latitude and assessment.longitude:
            props = {"id": assessment.koboid}

            if assessment.principal_photo:
                props.update({"image0": image_url(assessment.principal_photo)})
            else:
                props.update({"image0": "None"})

            if assessment.plan_photo:
                props.update({"image1": image_url(assessment.plan_photo)})
            else:
                props.update({"image1": "None"})

            # additional_photos = assessment.images()

            # for index, photo in enumerate(additional_photos):
            #     ind = str(index + 2)
            #     if photo:
            #         props.update({f"image{ind}": image_url(photo)})
            #     else:
            #         props.update({f"image{ind}": "None"})

            my_point = Point((float(assessment.longitude), float(assessment.latitude)))
            my_feature = Feature(geometry=Point(my_point), properties=props)
            data.append(my_feature)

    return FeatureCollection(data)


@app.get(
    "/geojsonv2",
    tags=["Geospatial Data"],
    summary="Returns a GeoJSON feature collection with associated assessment images. Uses the Miyamoto database.",
)
async def get_geojson_miyamoto(start: int = 0, limit: int = 10):
    results = await geo_json_lookup(start, limit)
    if results:
        final_json: FeatureCollection = await new_build_geojson(results)
        return final_json

    raise HTTPException(404, "Could not build GeoJson at this time.")


# async def collect_download(start: int, limit: int, commune: str = None):
#     if commune:
#         results = collection.find({}).skip(start).limit(limit)
#     else:
#         results = collection.find({}).skip(start).limit(limit)

#     json_string = json_util.dumps(results)
#     json_obj = json.loads(json_string)
#     data1 = pd.json_normalize(json_obj)
#     csv = data1.to_csv("FileName.csv")


# @app.get(
#     "/download",
#     tags=["Files/Downloads"],
#     summary="Download Assessment Data",
# )
# async def report(
#     filetype: str = "xls", start: int = 0, limit: int = 10, commune: str = None
# ):
#     if filetype:
#         if filetype == "xls":
#             thefile = await collect_download(start, limit, commune)
#             FileResponse(path="c:/", filename="test.xls", media_type="text/mp4")


async def lookup_assessment_by_qr(qrcode: str):

    result = collection.find_one(
        {
            "Veuillez utiliser la camera arrière de la tablette pour scanner le QR Code du Batiment": qrcode
        }
    )
    if result:
        return parse_json(result)

    raise HTTPException(status_code=404, detail="No assessment with that ID.")


@app.get("/assessment-data/qr")
async def get_assessment_by_qr(
    qrcode: str, assessment=Depends(lookup_assessment_by_qr)
):
    return assessment


@app.get("/dashboard")
async def get_assessment_by_qr(
    request: Request,
    response_class=HTMLResponse,
):
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "data": {}}
    )
