from .production import Settings as ProductionSettings


class Settings(ProductionSettings):
    ENVIRONMENT = "staging"
