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


class E0002_NombreDEtages(BaseModel):
    number_double: str


class Date(BaseModel):
    number_long: str


class DateDeLEnquete(BaseModel):
    date: Date


class ID(BaseModel):
    oid: str


class Index(BaseModel):
    number_int: int


class Assessment2(BaseModel):
    id: ID
    start: DateDeLEnquete
    end: DateDeLEnquete
    today: DateDeLEnquete
    username: str
    deviceid: str
    phonenumber: str
    survey_date: Optional[DateDeLEnquete] = Field(None, alias="Date de l'enquete")
    division: Optional[str] = Field(None, alias="B-0000 - Division")
    engineer_name: Optional[str] = Field(None, alias="B-0001 - Nom des ingénieurs")
    engineer_name: Optional[str] = Field(None, alias="B-0001 - Nom des ingénieurs")
    organisation_institution: str
    organization: Optional[str] = Field(None, alias="Organisation / Institution")
    veuillez_préciser_le_nom_de_l_organisation_que_vous_représentez: str
    ce_batiment_a_t_il_déjà_fait_l_objet_d_une_évaluation_rapide: str
    d_0001_dans_quel_département_le_batiment_est_situé: str
    d_0002_dans_quelle_commune: str
    adresse_du_bâtiment: str
    coordonnées_gps_6_m_près_max_du_bâtiment: str
    coordonnées_gps_6_m_près_max_du_bâtiment_latitude: E0002_NombreDEtages
    coordonnées_gps_6_m_près_max_du_bâtiment_longitude: E0002_NombreDEtages
    coordonnées_gps_6_m_près_max_du_bâtiment_altitude: E0002_NombreDEtages
    coordonnées_gps_6_m_près_max_du_bâtiment_precision: E0002_NombreDEtages
    nom_de_l_établissement_institution_facultatif: str
    veuillez_utiliser_la_camera_arrière_de_la_tablette_pour_scanner_le_qr_code_du_batiment: str
    nom_du_batiment_facultatif: str
    photo_de_la_façade_principale: str
    ce_bâtiment_est_il_l_édifice_principal_de_la_propriété_ou_est_il_dépendant_d_un_autre_bâtiment: str
    veuillez_utiliser_la_camera_arrière_de_la_tablette_pour_scanner_le_qr_code_du_batiment_principal_dont_dépend_le_batiment_que_vous_évaluez: str
    nom_de_la_personne_contact_facultatif: str
    numéro_de_téléphone_facultatif: E0002_NombreDEtages
    ce_batiment_est_il_complètement_effondré: str
    e_0001_type_d_inspection: str
    pourquoi_l_inspection_intérieure_n_a_pu_être_réalisée: str
    note_reprogrammation: str
    e_0002_nombre_d_etages: E0002_NombreDEtages
    e_0003_nombre_de_sous_sol: E0002_NombreDEtages
    e_0004_type_de_structure: str
    e_0005_type_de_plancher: str
    e_0006_type_de_toiture: str
    e_0006_type_de_toiture_acier_tole: E0002_NombreDEtages
    e_0006_type_de_toiture_beton_armé: E0002_NombreDEtages
    e_0006_type_de_toiture_bois_tole: E0002_NombreDEtages
    e_0006_type_de_toiture_paille: E0002_NombreDEtages
    e_0006_type_de_toiture_autre: E0002_NombreDEtages
    e_0007_type_de_mur: str
    e_0007_type_de_mur_beton_armé: E0002_NombreDEtages
    e_0007_type_de_mur_bloc_non_armé: E0002_NombreDEtages
    e_0007_type_de_mur_bloc_armé: E0002_NombreDEtages
    e_0007_type_de_mur_maçonnerie_de_roche: E0002_NombreDEtages
    e_0007_type_de_mur_briques: E0002_NombreDEtages
    e_0007_type_de_mur_bois_maçonnerie: E0002_NombreDEtages
    e_0007_type_de_mur_clissage: E0002_NombreDEtages
    e_0007_type_de_mur_autre: E0002_NombreDEtages
    f_0001_surperficie_approximative_en_m: E0002_NombreDEtages
    f_0002_nombre_de_résidence_ou_patients_élèves_employés: E0002_NombreDEtages
    f_0003_nombre_de_locaux_non_habitables: E0002_NombreDEtages
    f_0004_type_d_occupation: str
    g_0001_bâtiment_de_type_gouvernemental_veuillez_sélectionner: str
    g_0002_bâtiment_de_type_école_veuillez_sélectionner: str
    g_0003_bâtiment_de_type_sanitaire_veuillez_sélectionner: str
    g_0004_bâtiment_de_type_commercial_veuillez_sélectionner: str
    confession_religieuse: str
    g_0005_bâtiment_effondré_partiellement_effondré_ou_déplacé_ou_étage_penché_pourcentage: str
    g_0006_mur_intérieur_et_extérieur_fissuré_des_murs_fissuré_aux_murs_total: str
    g_0007_mur_intérieur_et_extérieur_effondré: str
    g_0008_colonnes_pilastres_et_corbeaux_fissurés_et_émiettes: str
    g_0009_dalles_poutres_solives_fissurées_et_écaillées: str
    h_0001_parapets_fermes_terrasses_et_escaliers_endommagés: str
    h_0002_fissures_ou_mouvement_de_sol: str
    h_0003_dommage_estimé: str
    h_0004_barricades_nécessaires_dans_la_zone: str
    h_0005_expertise_détaillée_recommandée: str
    h_0006_observations_facultatif: str
    h_0007_irrégularités_verticales: str
    h_0007_irrégularités_verticales_aucune: E0002_NombreDEtages
    h_0007_irrégularités_verticales_etage_mou: E0002_NombreDEtages
    h_0007_irrégularités_verticales_denivelés: E0002_NombreDEtages
    h_0007_irrégularités_verticales_murs_de_cisaillement_couplés: E0002_NombreDEtages
    h_0007_irrégularités_verticales_colonnes_raccourcis: E0002_NombreDEtages
    h_0007_irrégularités_verticales_martelement_de_batiments_adjacents: E0002_NombreDEtages
    h_0007_irrégularités_verticales_aucune_irrégularité: E0002_NombreDEtages
    i_0001_autres_recommandations_ou_restrictions_facultatif: str
    i_0002_date_de_début_de_construction: str
    i_0003_date_de_travaux_importants_de_rénovation: str
    i_0004_sol_de_l_emplacement: str
    i_0005_relief_du_terrain: str
    i_0006_emplacement_du_bâtiment: str
    i_0007_fondations: str
    i_0008_forme_en_plan: str
    i_0010_danger_causé_par_les_environnements_extérieurs_mettant_en_cause_l_utilisation_du_bâtiment_facultatif: str
    i_0011_photo_de_la_menace_externe_observee_facultatif: str
    j_0001_prise_de_vue_1_facultatif: str
    j_0002_prise_de_vue_2_facultatif: str
    j_0003_prive_de_vue_3_facultatif: str
    j_0004_prise_de_vue_4_facultatif: str
    j_0005_prise_de_vue_5_facultatif: str
    j_0006_prise_de_vue_6_facultatif: str
    k_0001_estimation_des_dommages_h_0003: str
    k_0002_effondrement_du_bâtiment_g_0005: str
    k_0003_fissure_mur_intérieur_et_extérieur_g_0006: str
    k_0004_effondrement_mur_intérieur_et_extérieur_g_0007: str
    k_0005_colonnes_pilastres_et_corbeaux_fissurés_et_emiettés_g_0008: str
    k_0006_dalles_poutres_solives_fissurées_et_écaillées_g_0009: str
    k_0007_parapets_fermes_terrasses_et_escaliers_endommagés_h_0001: str
    k_0008_deterioration_du_batiment: str
    k_0009_fissures_ou_mouvement_de_sol_h_0004: str
    k_0010_sol_de_l_emplacement_i_0004: str
    k_0011_inclinaison_de_construction_i_0005: str
    k_0012_emplacement_du_batiment_i_0006: str
    k_0013_irregularités_verticales_i_0009: str
    k_0014_signalisation_du_bâtiment: str
    k_0014_b_ce_batiment_est_il_réparable_ou_à_réparer: str
    k_0015_justification_de_la_signalisation_si_nécessaire: str
    no_niveau: str
    hidden: str
    l_enquête_est_maintenant_terminée_merci_pour_votre_disponibilité_et_vos_réponses_à_nos_questions: str
    version: str
    welcome9_version: str
    version_001: str
    version_002: str
    version_003: str
    version_004: str
    version_005: str
    k_0014_b_ce_batiment_tagué_rouge_est_il_réparable: str
    veuillez_scanner_le_code_du_batiment: str
    evaluation_détaillée: str
    plan_du_rez_de_chaussée: str
    code_lu: str
    nombre_element: str
    code_du_batiment: str
    plan_de_l_etage: str
    nombre_element_eta: str
    koboid: Index
    uuid: str
    submission_time: DateDeLEnquete
    validation_status: str
    notes: str
    status: str
    submitted_by: str
    tags: str
    index: Index
