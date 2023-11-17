from pydantic import BaseSettings


class Config(BaseSettings):
    temp_dir: str=f"content/temp/"
    db_dir: str=f'sqlite:///content/switches.db'
    file_dir: str=f'content/file/'


    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


app_config = Config()