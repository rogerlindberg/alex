"""
Retrieve PlannedWorkshift information from the Lifecare system
for our Tieto users.
"""

import json
from datetime import (
    date,
    time,
    datetime,
    timedelta,
    timezone,
)
from zoneinfo import ZoneInfo

from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import aliased
from sqlalchemy.orm.session import Session

from db import (
    DbRespondent,
    DbRespondentPlan,
    DbRespondentSetting,
    DbOrganisationSetting,
    NotAuthorizedError,
)

from hshlib.constants import EventLogId
from hshlib.environment import is_prod_version

from openapi_server.controllers.controllogger import ControlLogger
from openapi_server.controllers.respondents.user_applications.tieto.utils import (
    clean_personnel_name,
    get_last_name_initial,
)
from hshlib.environment import is_not_controller_test
from openapi_server.tieto_api.common.event_logging import (
    eventlog_error,
    eventlog_info,
)
from openapi_server.controllers.common import get_org_id_or_none
from openapi_server.tieto_api.common.rest import Api
from openapi_server.controllers.organisations.crud import get_organisations_by_code


CONTROLLER_LOGGER_NAME = "fetch-workshifts"
log_ep1 = ControlLogger(f"{CONTROLLER_LOGGER_NAME}-ep1").log
log_ep1.setLevel("DEBUG")


class Workshift:
    def __init__(
        self,
        revoked,
        respondent_id=None,
        start_tm=None,
        duration=None,
        plan_id=None,
        activity_id=None,
        activity_name=None,
        description=None,
        modification_tm=None,
        personnel_name=None,
    ):
        self.revoked = revoked
        self.respondent_id = respondent_id
        self.start_tm = start_tm
        self.duration = duration
        self.plan_id = plan_id
        self.activity_id = activity_id
        self.activity_name = activity_name
        self.description = description
        self.modification_tm = modification_tm
        self.personnel_name = personnel_name


def fetch_planned_workshifts(s: Session, organisation_code: str, test=False, token_info: dict = None):
    """
    Code to implement
    1) Get organisation from organisation_code
    2) Validate organisation against token_info
    3) Remove old records from table respondent_plan
    4) Get last update-time from organisation_setting
    5) Get respondents to update
    6) Retrieve respondents PersonId
    7) Get planned workshifts from tieto system
    8) Add new information to table respondent_plan
    9) Save last update-time

    """
    try:
        # 1)
        org = get_organisations_by_code(s, organisation_code, token_info)

        # 2)
        _validate_org(org, token_info)

        # 3)
        _remove_old_plans(s)

        # 4)
        last_update_time, default_last_update_time = _get_last_update_time(s, org)

        # 5)
        respondents = _get_respondents_to_update(s)

        # 6)
        respondents = _add_person_id(org, respondents, test)

        # 7)
        if len(respondents) > 0:
            workshifts, last_modification_tm = _get_planned_workshifts(s, org, last_update_time, respondents, test)
            if len(workshifts) > 0:
                # 8)
                _update_respondent_plan(s, org, workshifts)
            else:
                log_debug("No workshifts for update found")
            # 9)
            _save_last_update_time(s, org, last_modification_tm, default_last_update_time)
        else:
            log_debug("No respondents found. Aborting without action!")
    except (NotAuthorizedError, NoResultFound):
        raise
    except Exception as ex:
        log_error("Aborting due to exception")
        log_error(str(ex))
    return "OK", 200


def _validate_org(org, token_info):
    org_id = get_org_id_or_none(token_info)
    if org_id not in (0, org.id):
        raise NotAuthorizedError(f"org-id not in {(0, org.id)}")


def _remove_old_plans(s: Session):
    cutoff_date = date.today() - timedelta(days=1)
    (
        s.query(DbRespondentPlan)
        .filter(func.date(DbRespondentPlan.start_tm) < cutoff_date)
        .delete(synchronize_session=False)
    )
    s.commit()


def _get_last_update_time(s: Session, org):
    # Hämta värdet från databasen
    tm_str = (
        s.query(DbOrganisationSetting.value)
        .filter(DbOrganisationSetting.organisation_id == org.id)
        .filter(DbOrganisationSetting.attribute == "last_workshift_update_time")
        .scalar()
    )

    if tm_str:
        # Om värdet finns, konvertera från ISO-sträng till datetime
        tm = datetime.fromisoformat(tm_str)
        # Om det inte är timezone-aware, gör det UTC-aware
        if tm.tzinfo is None:
            tm = tm.replace(tzinfo=timezone.utc)
    else:
        # Default = 3 dagar tillbaka i UTC
        tm = datetime.now(timezone.utc) - timedelta(days=3)

    # Beräkna tm + something
    tm_plus = tm + timedelta(minutes=5)
    log_debug(f"last_update_time: {tm}q")
    log_debug(f"last_update_time +: {tm_plus}")

    return tm, tm_plus


def _get_respondents_to_update(s: Session):
    # Alias för DbRespondentSetting
    use_plan = aliased(DbRespondentSetting)
    ext_id = aliased(DbRespondentSetting)
    respondents = (
        s.query(DbRespondent.id, ext_id.value)
        .join(use_plan, DbRespondent.id == use_plan.respondent_id)
        .join(ext_id, DbRespondent.id == ext_id.respondent_id)
        .filter(
            use_plan.attribute == "use_plan",
            use_plan.value == "true",
            ext_id.attribute == "tieto_id",
            ext_id.value != "fake",
        )
    ).all()
    log_debug(f"{len(respondents)} nbr of respondents found.")
    return respondents


def _add_person_id(org, respondents, test):
    if test:
        return _add_person_id_from_lifecare(org, respondents, test)
    elif is_prod_version():
        log_debug("Collect Clients from Lifecare!")
        return _add_person_id_from_lifecare(org, respondents)
    else:
        # Fake Pnr. It's not used in test environments!
        return [(respondent_id, tieto_id, 0) for respondent_id, tieto_id in respondents]


def _add_person_id_from_lifecare(org, respondents, test=False):
    if test:
        api = Api.create_null_api(org.code, response=test_response())
    else:
        api = Api(org.code)
    collector = []
    for respondent_id, tieto_id in respondents:
        path = "/api/v1/clients"
        params = {"q": f"Id={tieto_id}"}
        response = api.get(path, params)
        if isinstance(response, Exception):
            raise response
        if response.status_code == 200:
            try:
                data = json.loads(_replace_uncicodes(response.json()))
                pnr = data[0].get("PersonId")
                collector.append((respondent_id, tieto_id, pnr))
            except Exception:
                log_error(f"Could not find PersonId in data: {response.json()}", org.id)
        else:
            log_error(
                f"Could not find Client with Tieto-Id {tieto_id} status_code:{response.status_code}!", org_id=org.id
            )
            if response.status_code >= 500:
                log_error(
                    f"Response {response.status_code}: headers={response.headers}, text={response.text[:500]}...",
                    org_id=org.id,
                )
    return collector


def test_response():
    class Resp:
        @property
        def status_code(self):
            return 200

        def json(self):
            return [
                {
                    "Active": True,
                    "Addresses": [
                        {
                            "CareOf": "",
                            "City": "JÄRFÄLLA",
                            "Country": "Sverige",
                            "EntryCode": "5637",
                            "Protected": False,
                            "StreetAddress": "Kopparvägen 29 Lgh 1802",
                            "Type": "Home",
                            "ZipCode": "17672",
                        }
                    ],
                    "Deleted": False,
                    "Deregistration": None,
                    "Emails": [],
                    "FirstName": "Conny Allan",
                    "FullName": "Conny Allan Eriksson",
                    "Id": 6020623,
                    "KeyCode": "222560",
                    "LastName": "Eriksson",
                    "MaritalStatus": "Skild",
                    "PersonId": "194808031019",
                    "Phones": [{"PhoneNumber": "0708481879", "Protected": False, "Type": "Home"}],
                    "ProtectedRegistration": False,
                    "UpdateTime": "2025-10-22T00:00:00",
                }
            ]

    return Resp()


def _replace_uncicodes(json_text):
    # Gör en dump utan att escapa icke-ASCII
    json_str = json.dumps(json_text, indent=4, ensure_ascii=False)
    # Konvertera till Latin-1-bytes
    latin1_bytes = json_str.encode("utf-8", errors="replace")
    # Om du vill ha en Latin-1-sträng (inte bytes)
    latin1_str = latin1_bytes.decode("utf-8", errors="replace")
    return latin1_str


def _get_planned_workshifts(s: Session, org, last_update_time, respondents, test):
    if is_prod_version():
        log_debug("Workshifts collected from Lifecare!")
        return _get_planned_workshifts_from_lifecare(org, last_update_time, respondents, test)
    else:
        log_debug("Workshifts are faked!")
        return _get_faked_workshifts(s, respondents)


def _get_planned_workshifts_from_lifecare(org, last_update_time, respondents, test):
    if test:
        api = Api.create_null_api(org.code, response=test_plans_response())
    else:
        api = Api(org.code)
    path = "/api/v1/planned_workshifts"
    params = {"modifiedTime": last_update_time}
    result = []
    last_modification_tm = None
    response = api.get(path, params)
    if isinstance(response, Exception):
        raise response
    if response.status_code == 200:
        workshifts = json.loads(_replace_uncicodes(response.json()))
        log_debug(f"Number of workshifts found: {len(workshifts)}")
        if len(workshifts) > 0:
            result, last_modification_tm = _process_planning_result(respondents, workshifts)
    else:
        log_error(f"Could not find workshifts: {last_update_time} status-code:{response.status_code}!", org_id=org.id)
    return result, last_modification_tm


def test_plans_response():
    class Resp:
        @property
        def status_code(self):
            return 200

        def json(self):
            jakobsberg3 = "Jakobsberg 3"
            tornerplatsen28 = "Tornerplatsen 28"
            jarfalla = "J\u00e4rf\u00e4lla"
            jarfalla2 = "J\u00c4RF\u00c4LLA"
            kvartalsvagen24 = "KVARTALSV\u00c4GEN 24"
            lisen = "Lisen Blomdahl"
            ny42 = "Ny 42"
            sol = "SoL St\u00f6d i hemmet dag"
            return [
                {
                    "Id": "2534187:HC:R",
                    "ModificationTime": "2025-10-01T11:05:00.15Z",
                    "PlanningUnitId": None,
                    "StartTime": "0001-01-01T00:00:00",
                    "EndTime": "0001-01-01T00:00:00",
                    "TravelTimeHome": "00:00:00",
                    "StartPosition": None,
                    "EndPosition": None,
                    "TypeOfTransportation": "Unknown",
                    "PlannedActivities": [],
                    "Personnel": None,
                    "IsRevoked": True,
                },
                {
                    "Id": "2521776:HC:R",
                    "ModificationTime": "2025-10-01T11:07:44.883Z",
                    "PlanningUnitId": jakobsberg3,
                    "StartTime": "2025-10-01T07:45:00",
                    "EndTime": "2025-10-01T14:00:00",
                    "TravelTimeHome": "00:00:00",
                    "StartPosition": {
                        "Address": {"StreetAddress": tornerplatsen28, "ZipCode": " 177 67", "City": jarfalla},
                        "Coordinate": {
                            "Latitude": 59.4224662458464,
                            "Longitude": 17.839343383433,
                            "CoordinateSystem": "WGS84",
                        },
                        "DetailText": "",
                    },
                    "EndPosition": {
                        "Address": {"StreetAddress": tornerplatsen28, "ZipCode": " 177 67", "City": jarfalla},
                        "Coordinate": {
                            "Latitude": 59.4224662458464,
                            "Longitude": 17.839343383433,
                            "CoordinateSystem": "WGS84",
                        },
                        "DetailText": "",
                    },
                    "TypeOfTransportation": "Bicycle",
                    "PlannedActivities": [
                        {
                            "Id": "23468767:HC:J",
                            "PlanningUnitId": jakobsberg3,
                            "StartTime": "2025-10-01T07:45:00",
                            "Duration": "00:20:00",
                            "TraveltimeToActivity": "00:00:00",
                            "ActivityName": "Uppstart",
                            "Description": "",
                            "IsMonitored": False,
                            "MedicalReminder": False,
                            "TypeOfPlannedActivity": "MiscPersonnelJob",
                            "StartPosition": {
                                "Address": {"StreetAddress": tornerplatsen28, "ZipCode": " 177 67", "City": jarfalla},
                                "Coordinate": {
                                    "Latitude": 59.4224662458464,
                                    "Longitude": 17.839343383433,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "EndPosition": {
                                "Address": {"StreetAddress": tornerplatsen28, "ZipCode": " 177 67", "City": jarfalla},
                                "Coordinate": {
                                    "Latitude": 59.4224662458464,
                                    "Longitude": 17.839343383433,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "ChangeOfTransportation": None,
                            "Client": None,
                            "KeyInfos": [],
                            "ServiceItems": [],
                        },
                        {
                            "Id": "23554218:HC:J",
                            "PlanningUnitId": jakobsberg3,
                            "StartTime": "2025-10-01T08:13:00",
                            "Duration": "00:30:00",
                            "TraveltimeToActivity": "00:07:00",
                            "ActivityName": "Morgon",
                            "Description": "Omv\u00e5rdnad morgon\nG\u00f6r frukost   , b\u00e4dda s\u00e4ngen ,plocka disken  sopa eller dammsug om det behovs  och sl\u00e4ng sopor .",
                            "IsMonitored": False,
                            "MedicalReminder": False,
                            "TypeOfPlannedActivity": "Visit",
                            "StartPosition": {
                                "Address": {"StreetAddress": kvartalsvagen24, "ZipCode": "17763", "City": jarfalla2},
                                "Coordinate": {
                                    "Latitude": 59.421338938304,
                                    "Longitude": 17.8214684748293,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "EndPosition": {
                                "Address": {"StreetAddress": kvartalsvagen24, "ZipCode": "17763", "City": jarfalla2},
                                "Coordinate": {
                                    "Latitude": 59.421338938304,
                                    "Longitude": 17.8214684748293,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "ChangeOfTransportation": None,
                            "Client": {
                                "PlanningUnitId": jakobsberg3,
                                "Addresses": None,
                                "Phones": None,
                                "Emails": None,
                                "PersonId": "194808031019",
                                "FirstName": "Lisen",
                                "LastName": "Blomdahl",
                                "FullName": lisen,
                            },
                            "KeyInfos": [
                                {
                                    "TypeOfKeyInfo": "ClientKeyNumber",
                                    "TypeOfKeyInfoLocalized": "Nyckelnummer",
                                    "Value": ny42,
                                }
                            ],
                            "ServiceItems": [
                                {
                                    "Type": {"Code": 559, "Text": "IBIC-Omv\u00e5rdnadspaket morgon"},
                                    "Category": {"Code": 88, "Text": sol},
                                },
                                {
                                    "Type": {"Code": 576, "Text": "IBIC-Frukost/mellanm\u00e5l/kv\u00e4llsm\u00e5l"},
                                    "Category": {"Code": 88, "Text": sol},
                                },
                            ],
                        },
                        {
                            "Id": "23587042:HC:J",
                            "PlanningUnitId": jakobsberg3,
                            "StartTime": "2025-10-01T08:44:00",
                            "Duration": "01:30:00",
                            "TraveltimeToActivity": "00:00:00",
                            "ActivityName": "St\u00e4d",
                            "Description": "",
                            "IsMonitored": False,
                            "MedicalReminder": False,
                            "TypeOfPlannedActivity": "Visit",
                            "StartPosition": {
                                "Address": {"StreetAddress": kvartalsvagen24, "ZipCode": "17763", "City": jarfalla2},
                                "Coordinate": {
                                    "Latitude": 59.421338938304,
                                    "Longitude": 17.8214684748293,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "EndPosition": {
                                "Address": {"StreetAddress": kvartalsvagen24, "ZipCode": "17763", "City": jarfalla2},
                                "Coordinate": {
                                    "Latitude": 59.421338938304,
                                    "Longitude": 17.8214684748293,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "ChangeOfTransportation": None,
                            "Client": {
                                "PlanningUnitId": jakobsberg3,
                                "Addresses": None,
                                "Phones": None,
                                "Emails": None,
                                "PersonId": "195502183089",
                                "FirstName": "Lisen",
                                "LastName": "Blomdahl",
                                "FullName": lisen,
                            },
                            "KeyInfos": [
                                {
                                    "TypeOfKeyInfo": "ClientKeyNumber",
                                    "TypeOfKeyInfoLocalized": "Nyckelnummer",
                                    "Value": ny42,
                                }
                            ],
                            "ServiceItems": [
                                {
                                    "Type": {"Code": 565, "Text": "IBIC-St\u00e4dning 3 r o k"},
                                    "Category": {"Code": 88, "Text": sol},
                                }
                            ],
                        },
                        {
                            "Id": "23587319:HC:J",
                            "PlanningUnitId": jakobsberg3,
                            "StartTime": "2025-10-01T10:15:00",
                            "Duration": "01:10:00",
                            "TraveltimeToActivity": "00:00:00",
                            "ActivityName": "Ledsagarservice",
                            "Description": "promenad st\u00f6tta henne med n\u00e5got hon beh\u00f6ver \nsocialsamvaro",
                            "IsMonitored": False,
                            "MedicalReminder": False,
                            "TypeOfPlannedActivity": "Visit",
                            "StartPosition": {
                                "Address": {"StreetAddress": kvartalsvagen24, "ZipCode": "17763", "City": jarfalla2},
                                "Coordinate": {
                                    "Latitude": 59.421338938304,
                                    "Longitude": 17.8214684748293,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "EndPosition": {
                                "Address": {"StreetAddress": kvartalsvagen24, "ZipCode": "17763", "City": jarfalla2},
                                "Coordinate": {
                                    "Latitude": 59.421338938304,
                                    "Longitude": 17.8214684748293,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "ChangeOfTransportation": None,
                            "Client": {
                                "PlanningUnitId": jakobsberg3,
                                "Addresses": None,
                                "Phones": None,
                                "Emails": None,
                                "PersonId": "195502183089",
                                "FirstName": "Lisen",
                                "LastName": "Blomdahl",
                                "FullName": lisen,
                            },
                            "KeyInfos": [
                                {
                                    "TypeOfKeyInfo": "ClientKeyNumber",
                                    "TypeOfKeyInfoLocalized": "Nyckelnummer",
                                    "Value": ny42,
                                }
                            ],
                            "ServiceItems": [
                                {
                                    "Type": {"Code": 43, "Text": "Ledsagning"},
                                    "Category": {"Code": 12, "Text": "SoL Ledsagning"},
                                }
                            ],
                        },
                        {
                            "Id": "23554474:HC:J",
                            "PlanningUnitId": jakobsberg3,
                            "StartTime": "2025-10-01T11:25:00",
                            "Duration": "00:15:00",
                            "TraveltimeToActivity": "00:00:00",
                            "ActivityName": "F\u00f6rmiddag",
                            "Description": "",
                            "IsMonitored": False,
                            "MedicalReminder": False,
                            "TypeOfPlannedActivity": "Visit",
                            "StartPosition": {
                                "Address": {"StreetAddress": kvartalsvagen24, "ZipCode": "17763", "City": jarfalla2},
                                "Coordinate": {
                                    "Latitude": 59.421338938304,
                                    "Longitude": 17.8214684748293,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "EndPosition": {
                                "Address": {"StreetAddress": kvartalsvagen24, "ZipCode": "17763", "City": jarfalla2},
                                "Coordinate": {
                                    "Latitude": 59.421338938304,
                                    "Longitude": 17.8214684748293,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "ChangeOfTransportation": None,
                            "Client": {
                                "PlanningUnitId": jakobsberg3,
                                "Addresses": None,
                                "Phones": None,
                                "Emails": None,
                                "PersonId": "195502183089",
                                "FirstName": "Lisen",
                                "LastName": "Blomdahl",
                                "FullName": lisen,
                            },
                            "KeyInfos": [
                                {
                                    "TypeOfKeyInfo": "ClientKeyNumber",
                                    "TypeOfKeyInfoLocalized": "Nyckelnummer",
                                    "Value": ny42,
                                }
                            ],
                            "ServiceItems": [
                                {
                                    "Type": {"Code": 584, "Text": "IBIC-F\u00f6rflyttning"},
                                    "Category": {"Code": 88, "Text": sol},
                                }
                            ],
                        },
                        {
                            "Id": "23468764:HC:J",
                            "PlanningUnitId": jakobsberg3,
                            "StartTime": "2025-10-01T11:48:00",
                            "Duration": "00:45:00",
                            "TraveltimeToActivity": "00:07:00",
                            "ActivityName": "Rast",
                            "Description": "",
                            "IsMonitored": False,
                            "MedicalReminder": False,
                            "TypeOfPlannedActivity": "Pause",
                            "StartPosition": {
                                "Address": {"StreetAddress": tornerplatsen28, "ZipCode": " 177 67", "City": jarfalla},
                                "Coordinate": {
                                    "Latitude": 59.4224662458464,
                                    "Longitude": 17.839343383433,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "EndPosition": {
                                "Address": {"StreetAddress": tornerplatsen28, "ZipCode": " 177 67", "City": jarfalla},
                                "Coordinate": {
                                    "Latitude": 59.4224662458464,
                                    "Longitude": 17.839343383433,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "ChangeOfTransportation": None,
                            "Client": None,
                            "KeyInfos": [],
                            "ServiceItems": [],
                        },
                        {
                            "Id": "23554505:HC:J",
                            "PlanningUnitId": jakobsberg3,
                            "StartTime": "2025-10-01T12:41:00",
                            "Duration": "00:45:00",
                            "TraveltimeToActivity": "00:07:00",
                            "ActivityName": "Lunch",
                            "Description": "",
                            "IsMonitored": False,
                            "MedicalReminder": False,
                            "TypeOfPlannedActivity": "Visit",
                            "StartPosition": {
                                "Address": {"StreetAddress": kvartalsvagen24, "ZipCode": "17763", "City": jarfalla2},
                                "Coordinate": {
                                    "Latitude": 59.421338938304,
                                    "Longitude": 17.8214684748293,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "EndPosition": {
                                "Address": {"StreetAddress": kvartalsvagen24, "ZipCode": "17763", "City": jarfalla2},
                                "Coordinate": {
                                    "Latitude": 59.421338938304,
                                    "Longitude": 17.8214684748293,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "ChangeOfTransportation": None,
                            "Client": {
                                "PlanningUnitId": jakobsberg3,
                                "Addresses": None,
                                "Phones": None,
                                "Emails": None,
                                "PersonId": "195502183089",
                                "FirstName": "Lisen",
                                "LastName": "Blomdahl",
                                "FullName": lisen,
                            },
                            "KeyInfos": [
                                {
                                    "TypeOfKeyInfo": "ClientKeyNumber",
                                    "TypeOfKeyInfoLocalized": "Nyckelnummer",
                                    "Value": ny42,
                                }
                            ],
                            "ServiceItems": [
                                {
                                    "Type": {"Code": 551, "Text": "IBIC-Toalettbes\u00f6k"},
                                    "Category": {"Code": 88, "Text": sol},
                                },
                                {
                                    "Type": {"Code": 562, "Text": "IBIC-Matdistribution"},
                                    "Category": {"Code": 88, "Text": sol},
                                },
                                {
                                    "Type": {"Code": 575, "Text": "IBIC-Enklare matlagning"},
                                    "Category": {"Code": 88, "Text": sol},
                                },
                                {
                                    "Type": {"Code": 576, "Text": "IBIC-Frukost/mellanm\u00e5l/kv\u00e4llsm\u00e5l"},
                                    "Category": {"Code": 88, "Text": sol},
                                },
                                {"Type": {"Code": 578, "Text": "IBIC-Disk"}, "Category": {"Code": 88, "Text": sol}},
                            ],
                        },
                        {
                            "Id": "23468765:HC:J",
                            "PlanningUnitId": jakobsberg3,
                            "StartTime": "2025-10-01T13:35:00",
                            "Duration": "00:15:00",
                            "TraveltimeToActivity": "00:07:00",
                            "ActivityName": "Dokumentation",
                            "Description": "",
                            "IsMonitored": False,
                            "MedicalReminder": False,
                            "TypeOfPlannedActivity": "MiscPersonnelJob",
                            "StartPosition": {
                                "Address": {"StreetAddress": tornerplatsen28, "ZipCode": " 177 67", "City": jarfalla},
                                "Coordinate": {
                                    "Latitude": 59.4224662458464,
                                    "Longitude": 17.839343383433,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "EndPosition": {
                                "Address": {"StreetAddress": tornerplatsen28, "ZipCode": " 177 67", "City": jarfalla},
                                "Coordinate": {
                                    "Latitude": 59.4224662458464,
                                    "Longitude": 17.839343383433,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "ChangeOfTransportation": None,
                            "Client": None,
                            "KeyInfos": [],
                            "ServiceItems": [],
                        },
                        {
                            "Id": "23468766:HC:J",
                            "PlanningUnitId": jakobsberg3,
                            "StartTime": "2025-10-01T13:50:00",
                            "Duration": "00:10:00",
                            "TraveltimeToActivity": "00:00:00",
                            "ActivityName": "Avslut",
                            "Description": "",
                            "IsMonitored": False,
                            "MedicalReminder": False,
                            "TypeOfPlannedActivity": "MiscPersonnelJob",
                            "StartPosition": {
                                "Address": {"StreetAddress": tornerplatsen28, "ZipCode": " 177 67", "City": jarfalla},
                                "Coordinate": {
                                    "Latitude": 59.4224662458464,
                                    "Longitude": 17.839343383433,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "EndPosition": {
                                "Address": {"StreetAddress": tornerplatsen28, "ZipCode": " 177 67", "City": jarfalla},
                                "Coordinate": {
                                    "Latitude": 59.4224662458464,
                                    "Longitude": 17.839343383433,
                                    "CoordinateSystem": "WGS84",
                                },
                                "DetailText": "",
                            },
                            "ChangeOfTransportation": None,
                            "Client": None,
                            "KeyInfos": [],
                            "ServiceItems": [],
                        },
                    ],
                    "Personnel": {
                        "PlanningUnitId": jakobsberg3,
                        "PersonId": "19821022-6885",
                        "FirstName": "Letensie",
                        "LastName": "Weldemichail",
                        "FullName": "Letensie Weldemichail",
                    },
                    "IsRevoked": False,
                },
            ]

    return Resp()


def _process_planning_result(persons, result):
    collector = []
    last_modification_tm = None
    for plan in result:
        mtm = plan.get("ModificationTime")
        if mtm is not None:
            last_modification_tm = mtm
        if plan.get("IsRevoked") == True:
            collector.append(Workshift(True, plan_id=plan.get("Id")))
        else:
            _process_planned_activities(collector, plan, persons)
    return collector, last_modification_tm


def _process_planned_activities(collector, plan, persons):
    pnrs = {pnr: rid for rid, tid, pnr in persons}
    for activity in plan.get("PlannedActivities"):
        try:
            if "Client" in activity and activity.get("Client") is not None:
                pnr = activity.get("Client").get("PersonId")
                if pnr in pnrs:
                    activity_name = fix_bad_chars(activity.get("ActivityName"))
                    # The doc implies the times are in UTC.
                    # Our tests shows that it may be local time
                    # let's try local time to so if it works better
                    # tm = datetime.fromisoformat(activity.get('StartTime')).replace(tzinfo=timezone.utc)
                    tm = datetime.fromisoformat(activity.get("StartTime")).replace(tzinfo=ZoneInfo("Europe/Stockholm"))
                    tm = tm + get_traveltime_delta(activity)
                    obj = Workshift(
                        False,
                        respondent_id=pnrs[pnr],
                        start_tm=tm,
                        duration=_minutes_from_duration(activity),
                        plan_id=plan.get("Id"),
                        activity_id=activity.get("Id"),
                        activity_name=activity_name or "",
                        description=activity.get("description") or "",
                        modification_tm=plan.get("ModificationTime"),
                        personnel_name=get_personnel_name(plan),
                    )
                    collector.append(obj)
        except Exception as ex:
            log_error(str(ex))


def get_traveltime_delta(activity):
    travel_time_to_activity = activity.get("TraveltimeToActivity") or "00:00:00"
    h, m, sec = map(int, travel_time_to_activity.split(":"))
    return timedelta(hours=h, minutes=m, seconds=sec)


def get_personnel_name(plan):
    name = plan.get("Personnel", {}).get("FirstName") or ""
    last_name = plan.get("Personnel", {}).get("LastName") or ""
    clean_name = clean_personnel_name(name)
    last_name_initial = get_last_name_initial(last_name)
    if last_name_initial:
        clean_name = f"{clean_name} {last_name_initial}"
    log_debug(f"Personnel name: {name}  Cleaned to: {clean_name}")
    return clean_name


def fix_bad_chars(s):
    """
    Sometimes the text contains a leading character with code 164!
    Don't know why!
    """
    try:
        if ord(s[0]) == 164:
            return s[1:]
    except Exception:
        pass
    return s


def _minutes_from_duration(plan: dict) -> int:
    """
    Convert a time to minutes.
    """
    duration = plan.get("Duration")
    t = datetime.strptime(duration, "%H:%M:%S")
    minutes = t.hour * 60 + t.minute + t.second // 60
    return minutes


def _get_faked_workshifts(s, respondents):
    collector = []
    for rid, tid, pnr in respondents:
        num_plans = s.query(DbRespondentPlan).filter(DbRespondentPlan.respondent_id == rid).count()
        if num_plans < 10:
            collector.append(
                Workshift(
                    revoked=False,
                    respondent_id=rid,
                    start_tm=datetime.combine(datetime.today().date(), time(hour=9, minute=15)).isoformat(),
                    duration=10,
                    plan_id="2507131:HC:R",
                    activity_id="23675051:HC:J",
                    activity_name="Morgonrutin",
                    description="",
                    modification_tm=datetime.combine(datetime.today().date(), time(hour=6)).isoformat(),
                    personnel_name="Anna Andersson",
                )
            )
            collector.append(
                Workshift(
                    revoked=False,
                    respondent_id=rid,
                    start_tm=datetime.combine(datetime.today().date(), time(hour=12, minute=7)).isoformat(),
                    duration=10,
                    plan_id="2507132:HC:R",
                    activity_id="23675052:HC:J",
                    activity_name="Lunch",
                    description="",
                    modification_tm=datetime.combine(datetime.today().date(), time(hour=6)).isoformat(),
                    personnel_name="Hans Bertil Karlsson",
                )
            )
            collector.append(
                Workshift(
                    revoked=False,
                    respondent_id=rid,
                    start_tm=datetime.combine(datetime.today().date(), time(hour=22, minute=12)).isoformat(),
                    duration=10,
                    plan_id="2507133:HC:R",
                    activity_id="23675053:HC:J",
                    activity_name="Nattmacka",
                    description="",
                    modification_tm=datetime.combine(datetime.today().date(), time(hour=6)).isoformat(),
                    personnel_name="Bo Ek",
                )
            )
    return collector, None


def _update_respondent_plan(s: Session, org, workshifts):
    # Separera revoked och adds
    revokes = [ws for ws in workshifts if ws.revoked]
    adds = _remove_duplicates([ws for ws in workshifts if not ws.revoked])

    # ⚡ Batch-delete
    log_debug(f"{len(revokes)} plans to revoke!")
    if revokes:
        plans_to_delete = [ws.plan_id for ws in revokes]
        deleted_count = (
            s.query(DbRespondentPlan)
            .filter(DbRespondentPlan.plan_id.in_(plans_to_delete))
            .delete(synchronize_session=False)
        )
        log_debug(f"Actually deleted rows: {deleted_count}")

    # ⚡ Batch-insert
    log_debug(f"{len(adds)} plans to add!")
    if adds:
        existing_keys = {
            (p.respondent_id, p.plan_id, p.activity_id)
            for p in s.query(DbRespondentPlan.respondent_id, DbRespondentPlan.plan_id, DbRespondentPlan.activity_id)
        }
        plans_to_add = [
            DbRespondentPlan(
                respondent_id=ws.respondent_id,
                start_tm=ws.start_tm,
                duration=ws.duration,
                plan_id=ws.plan_id,
                activity_id=ws.activity_id,
                activity_name=ws.activity_name,
                description=ws.description,
                personnel_name=ws.personnel_name,
                owner=org.id,
            )
            for ws in adds
            if (ws.respondent_id, ws.plan_id, ws.activity_id) not in existing_keys
        ]
        log_debug(f"{len(plans_to_add)} plans actually added!")
        s.add_all(plans_to_add)

    # Commit allt på en gång
    try:
        s.commit()
    except Exception as ex:
        print(str(ex))


def _remove_duplicates(workshifts):
    seen = set()
    unique_workshifts = []
    for ws in workshifts:
        key = (ws.respondent_id, ws.plan_id, ws.activity_id)
        if key not in seen:
            seen.add(key)
            unique_workshifts.append(ws)
    return unique_workshifts


def _save_last_update_time(s: Session, org, last_modification_tm, default_last_update_time):
    if last_modification_tm is None:
        log_debug("last_modification_tm is None!")
        last_modification_tm = default_last_update_time
        log_debug(f"Using default: {default_last_update_time}")

    # Kolla om attributet finns
    last_update_time = (
        s.query(DbOrganisationSetting)
        .filter(DbOrganisationSetting.organisation_id == org.id)
        .filter(DbOrganisationSetting.attribute == "last_workshift_update_time")
        .first()
    )

    if last_update_time is None:
        # Skapa nytt attribut (upsert)
        new_setting = DbOrganisationSetting(
            organisation_id=org.id, attribute="last_workshift_update_time", value=last_modification_tm
        )
        s.add(new_setting)
        s.commit()
    else:
        # Om det finns, uppdatera värdet om du vill
        last_update_time.value = last_modification_tm
        s.commit()
    log_debug(f"New Last modification time: {last_modification_tm}")


# ======================================================================================
# loggers
# ======================================================================================


def log_debug(msg):
    if is_not_controller_test():
        log_ep1.debug(msg)


def log_info(msg, org_id: int = 0) -> None:
    if is_not_controller_test():
        log_ep1.info(msg)
    eventlog_info(EventLogId.respondent_plans_inf, msg, owner=org_id)


def log_error(msg="", org_id: int = 0):
    if is_not_controller_test():
        log_ep1.error(msg)
    eventlog_error(EventLogId.respondent_plans_err, msg, owner=org_id)
