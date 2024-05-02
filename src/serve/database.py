from sqlalchemy import create_engine


def create_database_engine(echo: bool = False):
    engine = create_engine("sqlite:///predictions.sqlite", echo=echo)
    return engine
