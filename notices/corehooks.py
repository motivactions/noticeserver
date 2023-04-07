from server import hooks

# from push_notifications.api.rest_framework import (
#     APNSDeviceAuthorizedViewSet,
#     GCMDeviceAuthorizedViewSet,
#     WebPushDeviceAuthorizedViewSet,
# )


@hooks.register("API_V1_URL_PATTERNS")
def register_notices_urls():
    return "", "notices.api.v1.urls"


# @hooks.register("API_V1_ME_VIEWSET")
# def register_me_apnsdevice_viewset():
#     return {
#         "prefix": "apnsdevice",
#         "viewset": APNSDeviceAuthorizedViewSet,
#         "basename": "apnsdevice",
#     }


# @hooks.register("API_V1_ME_VIEWSET")
# def register_me_gcmdevice_viewset():
#     return {
#         "prefix": "gcmdevice",
#         "viewset": GCMDeviceAuthorizedViewSet,
#         "basename": "gcmdevice",
#     }


# @hooks.register("API_V1_ME_VIEWSET")
# def register_me_webpushdevice_viewset():
#     return {
#         "prefix": "webpushdevice",
#         "viewset": WebPushDeviceAuthorizedViewSet,
#         "basename": "webpushdevice",
#     }
