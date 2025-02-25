import os


def extend_superapp_settings(main_settings):
    main_settings['INSTALLED_APPS'] += [
        'superapp.apps.prelude_sms',
    ]
    main_settings['DEFAULT_FROM_SMS'] = os.environ.get('DEFAULT_FROM_SMS')
    main_settings['PRELUDE_API_TOKEN'] = os.environ.get('PRELUDE_API_TOKEN')

