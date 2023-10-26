from pydantic import BaseSettings


class Config(BaseSettings):
    temp_dir: str
    db_dir: str=f'sqlite:///axial.db'
    data_dir: str=''
    file_dir: str=''


    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


app_config = Config()