"""
On-board a Tieto client. If already exists update. If not active delete it.

The intended use case is that the epoller calls this function to onboard, update
or delete Tieto clients, after retrieving a client list
"""

import uuid

from sqlalchemy.orm.session import Session

from db import (
    DbOrganisationSetting,
    DbRespondent,
    DbRespondentSetting,
    DbRespondentInfo,
)


from hshlib.constants import (
    EventLogId,
    GrantRulePath,
)
from hshlib.exceptions import (
    DataError,
    EmailError,
    KeycloakError,
    PhoneError,
)
from openapi_server.controllers.authvalidator import (
    GetAuthValidator,
    GET,
)
from openapi_server.controllers.controllogger import ControlLogger
from hshlib.environment import is_not_controller_test
from openapi_server.models.tieto_client_model import TietoClientModel
from openapi_server.tieto_api.common.event_logging import (
    eventlog_error,
    eventlog_info,
)
from openapi_server.controllers.respondents.user_applications.admin.acceptapplication import (
    create_respondent,
    save_respondent_attributes,
)
from keycloak.exceptions import KeycloakPostError
from openapi_server.controllers.keycloak import (
    NullKeycloak,
    Keycloak,
)
from openapi_server.tieto_api.common.compose_sms import compose_onboard_sms
from openapi_server.tieto_api.common.send_sms import send_sms


CONTROLLER_LOGGER_NAME = "client-onboarding"
log_ep1 = ControlLogger(f"{CONTROLLER_LOGGER_NAME}-ep1").log
log_ep1.setLevel("DEBUG")


def onboard_tieto_client(s: Session, body: dict, test, token_info: dict = None) -> tuple[str, int]:
    """
    The epoller has collected all tieto clients that shall be onboarded, updated or deleted,
    and calls this API once for each client. And the reason for this is to avoid a server
    timeout (30 secs) if there are many clients to process.
    """
    try:
        log_debug(f"Onboard Tieto Clients. Testmode: {test}")
        model = create_model_from_input(body, token_info)
        ensure_valid_phone(model)
        ensure_valid_email(model)
        return onboard(s, model, test, token_info)
    except (DataError, EmailError, KeycloakError, PhoneError) as ex:
        return str(ex), 400


def create_model_from_input(body, token_info):
    """
    The epoller is always using org_id 0, so we have to modify the token info
    to contain the correct org_id.
    THe Keycloak routine needs a model.organisation attribute
    """
    model = TietoClientModel.from_dict(body)
    model.organisation = model.org_id
    model.uuid = generate_uuid()
    token_info["organisation"] = model.org_id
    return model


def generate_uuid():
    return str(uuid.uuid4())


def ensure_valid_phone(model):
    """
    >>> model = TietoClientModel(phone='46708123123')
    >>> ensure_valid_phone(model)

    >>> model = TietoClientModel(phone=None)
    >>> ensure_valid_phone(model)
    Traceback (most recent call last):
    ...
    hshlib.exceptions.PhoneError: Bad phone! Phone: 'None'

    >>> model = TietoClientModel(phone='  ')
    >>> ensure_valid_phone(model)
    Traceback (most recent call last):
    ...
    hshlib.exceptions.PhoneError: Bad phone! Phone: '  '
    """
    if model.phone is None or len(model.phone.strip()) == 0:
        log_error(f"Bad phone! Phone: '{model.phone}' ")
        raise PhoneError(f"Bad phone! Phone: '{model.phone}'")


def ensure_valid_email(model):
    """
    # doctest: +ELLIPSIS

    >>> model = TietoClientModel(email='46708123123')
    >>> ensure_valid_email(model)

    >>> model = TietoClientModel(email=None)
    >>> ensure_valid_email(model)
    Traceback (most recent call last):
    ...
    hshlib.exceptions.EmailError: Bad email! Email: 'None'

    >>> model = TietoClientModel(email='  ')
    >>> ensure_valid_email(model)
    Traceback (most recent call last):
    ...
    hshlib.exceptions.EmailError: Bad email! Email: '  '
    """
    if model.email is None or len(model.email.strip()) == 0:
        log_error(f"Bad email! Email: '{model.email}'")
        raise EmailError(f"Bad email! Email: '{model.email}'")


def onboard(s: Session, model: TietoClientModel, test, token_info):
    if client_exists_as_respondent(s, model, token_info):
        if model.deleted:
            return delete(s, model, token_info)
        else:
            return update(s, model, token_info)
    else:
        if model.active and not model.deleted:
            return create(s, model, test, token_info)
        else:
            return "Nothing to do", 200


def client_exists_as_respondent(s: Session, model: TietoClientModel, token_info):
    return model.id in get_ids_of_all_registered_tieto_users(s, model.org_id, token_info)


def get_ids_of_all_registered_tieto_users(session, org_id: int, token_info):
    """
    Return a list of tieto user id's for users that are already
    registered with Hsh.
    """
    owners = GetAuthValidator(session, token_info).get_valid_owners(GET, GrantRulePath.respondents)
    settings = (
        session.query(DbRespondentSetting)
        .join(DbRespondent, DbRespondent.id == DbRespondentSetting.respondent_id)
        .filter(DbRespondentSetting.attribute == "tieto_id")
        .filter(DbRespondent.owner.in_(owners))
        .all()
    )
    ids = [int(setting.value) for setting in settings if setting.value.strip().lstrip("-").isdigit()]
    return ids


def update(session, model: TietoClientModel, token_info):
    log_debug(f"Tieto client id: {model.id} found -> update")
    respondent = get_respondent_by_tieto_id(session, model, token_info)
    if respondent:
        log_debug(f"Update Tieto client id: {model.id} Respondent id: {respondent.id}")
        update_tieto_user(session, model, respondent, token_info)
        return respondent.id, 201
    raise DataError(f"Can't retrieve respondent for Tieto Client id: {model.id}")


def update_tieto_user(session, model: TietoClientModel, respondent, _token_info) -> None:
    respondent_info = session.query(DbRespondentInfo).filter(DbRespondentInfo.respondent_id == respondent.id).one()
    respondent_info.email = model.email
    respondent_info.phone = model.phone
    respondent_info.first_name = model.first_name
    respondent_info.last_name = model.last_name
    session.commit()
    log_debug(f"Tieto user: {model.id} respondent: {respondent.id} updated")


def delete(session, model: TietoClientModel, token_info):
    log_debug(f"Tieto client id: {model.id} found -> delete")
    respondent = get_respondent_by_tieto_id(session, model, token_info)
    if respondent:
        log_debug(f"Delete Tieto client id: {model.id} Respondent id: {respondent.id}")
        delete_tieto_respondent(session, model, respondent, token_info)
        return "Deleted", 204
    raise DataError(f"Can't retrieve respondent for Tieto Client id: {model.id}")


def delete_tieto_respondent(session, model, respondent, token_info) -> None:
    """
    It's problematic to import delete_respondent at top of the file due to
    circular imports. Therefore, we import it here.
    """
    from openapi_server.controllers.respondents.respondents import delete_respondent

    delete_respondent(session, respondent.id, token_info)
    log_debug(f"Tieto user: {model.id} respondent: {respondent.id} deleted")


def get_respondent_by_tieto_id(session, model, _token_info):
    respondent = (
        session.query(DbRespondent)
        .join(DbRespondentSetting, DbRespondent.id == DbRespondentSetting.respondent_id)
        .filter(DbRespondentSetting.attribute == "tieto_id")
        .filter(DbRespondentSetting.value == str(model.id))
        .filter(DbRespondent.owner == model.org_id)
        .first()
    )
    if respondent:
        log_debug(f"Respondent Retrieved id: {respondent.id}")
    else:
        log_debug("Respondent Not Found")
    return respondent


def create(session, model: TietoClientModel, test, token_info):
    log_debug(f"Create Tieto client id: {model.id}")
    create_keycloak_account(model, test)
    respondent = create_respondent(session, model, model.org_id, model.uuid, token_info)
    save_respondent_attributes(session, respondent.id, model)
    send_sms_to_respondent(session, model)
    log_debug(f"Respondent {respondent.id} created.")
    return respondent.id, 201


def send_sms_to_respondent(session, model):
    simulate_sms = do_simulate_sms(session, model.org_id)
    log_debug(f"Simulate sms: {simulate_sms}")
    recipient = model.phone
    message = compose_onboard_sms(model.email, model.first_time_pw)
    send_sms(message, recipient, simulate_sms)
    log_debug(f"Onboarding sms sent to {recipient}")


def do_simulate_sms(session, org_id: int):
    attribute_name = "simulate_sms"
    setting = (
        session.query(DbOrganisationSetting)
        .filter(DbOrganisationSetting.organisation_id == org_id)
        .filter(DbOrganisationSetting.attribute == attribute_name)
        .first()
    )
    if setting is None:
        return True
    else:
        return setting.value.lower() == "true"


def create_keycloak_account(model: TietoClientModel, test):
    try:
        keycloak = create_keycloak_user(model, model.uuid, test)
        model.first_time_pw = keycloak.user_pw
        log_debug(f"Keycloak account created: {model.email}")
    except KeycloakPostError as ex:
        log_error(f"Keycloak User {model.email}: {str(ex)}")
        raise KeycloakError("Failed to update Keycloak")


def create_keycloak_user(registered_user, uuid, test):
    if test:
        log_debug("Keycloak creation simulated")
        keycloak = NullKeycloak()
    else:
        log_debug("Real Keycloak creation")
        keycloak = Keycloak()
    keycloak.onboard(registered_user, uuid)
    return keycloak


# ======================================================================================
# loggers
# ======================================================================================


def log_debug(msg):
    if is_not_controller_test():
        log_ep1.debug(msg)


def log_info(msg, org_id: int = 0) -> None:
    if is_not_controller_test():
        log_ep1.info(msg)
    eventlog_info(EventLogId.onboard_client_inf, msg, owner=org_id)


def log_error(msg="", org_id: int = 0):
    if is_not_controller_test():
        log_ep1.error(msg)
    eventlog_error(EventLogId.onboard_client_err, msg, owner=org_id)
