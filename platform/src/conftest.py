def pytest_configure():
    from django.conf import settings

    drf_settings = getattr(settings, 'REST_FRAMEWORK', {}).copy()

    # Our tests rely on SessionAuthentication, but we only want JWT authentication for actual traffic
    # So, we add SessionAuthentication to the django settings just for pytest
    current_auth_classes = list(drf_settings.get('DEFAULT_AUTHENTICATION_CLASSES', []))
    session_auth_class = 'rest_framework.authentication.SessionAuthentication'

    if session_auth_class not in current_auth_classes:
        current_auth_classes.insert(0, session_auth_class)

    drf_settings['DEFAULT_AUTHENTICATION_CLASSES'] = tuple(current_auth_classes)
    settings.REST_FRAMEWORK = drf_settings
