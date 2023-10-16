from pydantic import BaseSettings


class Config(BaseSettings):
    tmp_dir: str
    db_dir: str=f'sqlite:///axial.db'
    import_dir: str


    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


app_config = Config()