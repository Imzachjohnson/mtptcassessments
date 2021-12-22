from pydantic import BaseModel, Field
from typing import List, Any, Optional
import secrets


class Attachment(BaseModel):
    download_url: Optional[str]
    download_medium_url: Optional[str]
    download_small_url: Optional[str]
    download_large_url: Optional[str]
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


class GeoAssessment(BaseModel):

    latitude: str = Field(
        None, alias="_Coordonnées GPS ( 6m près max du bâtiment)_latitude"
    )
    longitude: str = Field(
        None, alias="_Coordonnées GPS ( 6m près max du bâtiment)_longitude"
    )

    koboid: Optional[str]

    principal_photo: Optional[str] = Field(None, alias="Photo de la façade principale")
    plan_photo: Optional[str] = Field(None, alias="Plan du rez de chaussée")

    external_damage: Optional[str] = Field(
        None, alias="I-0011 Photo de la menace externe observee (Facultatif)"
    )

    additional_image_1: Optional[str] = Field(
        None, alias="J-0001 - Prise de vue 1 (facultatif)"
    )

    additional_image_2: Optional[str] = Field(
        None, alias="J-0002 - Prise de vue 2 (facultatif)"
    )

    additional_image_3: Optional[str] = Field(
        None, alias="J-0003 - Prive de vue 3 (facultatif)"
    )

    additional_image_4: Optional[str] = Field(
        None, alias="J-0004 - Prise de vue 4 (facultatif)"
    )

    additional_image_5: Optional[str] = Field(
        None, alias="J-0005 - Prise de vue 5 (facultatif)"
    )

    additional_image_6: Optional[str] = Field(
        None, alias="J-0006 - Prise de vue 6 (facultatif)"
    )

    def images(self):
        images = []

        if self.additional_image_1:
            images.append(self.additional_image_1)
        if self.additional_image_2:
            images.append(self.additional_image_2)
        if self.additional_image_3:
            images.append(self.additional_image_3)
        if self.additional_image_4:
            images.append(self.additional_image_4)
        if self.additional_image_5:
            images.append(self.additional_image_5)
        if self.additional_image_6:
            images.append(self.additional_image_6)
        return images

    def build(data):
        return Assessment(**data)


class GeoAssessmentList(BaseModel):
    assessments: List[GeoAssessment]

    def build(data):
        return GeoAssessmentList(**data)


class AssessmentList(BaseModel):
    assessments: Optional[List[Assessment]]


class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    organization: str
    admin: bool = False
    active: bool = True
    password: str
    api_key: str

    @property
    def user_info(self):
        return {
            "first_name": self.first_name,
            "email": self.email,
            "organization": self.organization,
            "admin": self.admin,
            "active": self.active,
        }
