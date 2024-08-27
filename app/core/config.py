from pydantic import BaseSettings


class Config(BaseSettings):
    temp_dir: str=f"data/temp/"
    db_dir: str=f'sqlite:///data/db/switches.db'
    file_dir: str=f'data/images/'
    image_cache_path: str=f'data/image_cache/'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


app_config = Config()

import os
os.makedirs(app_config.temp_dir, exist_ok=True)
os.makedirs(app_config.file_dir, exist_ok=True)
os.makedirs(app_config.image_cache_path, exist_ok=True)