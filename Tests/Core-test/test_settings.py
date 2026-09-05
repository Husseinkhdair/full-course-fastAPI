from Core.Settings import SettingsApp


settings = SettingsApp()

def test_settings():
    assert settings.mongodb_url is not None
    assert settings.mongodb_name is not None
    assert settings.collection_users is not None
    assert settings.postgre_url is not None
    
