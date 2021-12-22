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
from users import (
    admin_route,
    authenticate_user,
    create_user,
    get_user_by_api_key,
    get_current_user,
)

from pymongo import MongoClient

from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from helpers import parse_json
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from keys import Keys

# Database Connection
myclient = MongoClient(
    "mongodb+srv://zjohnson:Coopalex0912@cluster0.2amvb.mongodb.net/mtptcmiyamoto?retryWrites=true&w=majority"
)


# database
db = myclient["mtptcmiyamoto"]

# Assessment collection
collection = db["assessments"]

# Declare fast API
app = FastAPI(title="Miyamoto MTPTC Assessments", version="0.1.1", root_path="/")

# Used for HTML pages
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Kobo Api Information
API_URL = "https://kc.humanitarianresponse.info/api/v1/data/"

MEDIA_API_URL = "https://kc.humanitarianresponse.info/api/v1/media/"

FORM_ID = "894190"


# Append Kobo URL to images
def image_url(image: str):
    return f"https://kc.humanitarianresponse.info/attachment/large?media_file=btbmtptc/attachments/{image}"


# GeoJSON Route
@app.get(
    "/geojson/{api_key}",
    tags=["Geospatial Data"],
    summary="Returns a GeoJSON feature collection with associated assessment images. Uses the Kobo API and must include an API key.",
    deprecated=True,
)
async def get_geojson(api_key, start: int = 0, limit: int = 10):
    return convertogeojson(all_data_request(api_key, start, limit))


# Assessment data route
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
    token: str = Depends(Keys.OAUTH_URL),
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


# Stats Route
@app.get(
    "/assessment-data/stats/",
    tags=["Reporting"],
    summary="Returns a JSON response with various assessment data statistics.",
)
async def assessment_statistics(
    auth: str, validate=Depends(get_user_by_api_key), dashboard: bool = False
):
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


# Data for PowerBI reports
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


# Method to lookup and return assessment data for GeoJSON route
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
        return None


# Build a GeoJSON object
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


# V2 route for GEOJSON
@app.get(
    "/geojsonv2",
    tags=["Geospatial Data"],
    summary="Returns a GeoJSON feature collection with associated assessment images. Uses the Miyamoto database.",
)
async def get_geojson_miyamoto(
    auth: str, validate=Depends(get_user_by_api_key), start: int = 0, limit: int = 10
):
    results = await geo_json_lookup(start, limit)
    if results:
        final_json: FeatureCollection = await new_build_geojson(results)
        return final_json

    raise HTTPException(404, "Could not build GeoJson at this time.")


# Create User via API Key
@app.get("/create-user", include_in_schema=False)
async def create_user_route(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    organization: str,
    auth: str,
    admin: bool,
    validate=Depends(admin_route),
):
    user = await create_user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        organization=organization,
        admin=admin,
    )
    return user
    raise HTTPException(404, "Something went wrong.")


@app.get("/test", include_in_schema=False)
async def get_user(auth: str, validate=Depends(get_user_by_api_key)):
    user = await get_user_by_api_key(auth)
    return user


@app.post("/token", tags=["Authentication"])
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(404, "Invalid credentials")

    token = jwt.encode(user.user_info, Keys.JWT_SECRET)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/me", tags=["Users"], summary="Get the current user")
async def get_current(user: User = Depends(get_current_user)):
    return user
