from pydantic import BaseSettings


class Config(BaseSettings):
    temp_dir: str=f"data/temp/"
    db_dir: str=f'sqlite:///data/db/switches.db'
    file_dir: str=f'data/images/'
    image_cache_path: str=f'data/image_cache/'
    mode: str='master'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    def is_master(self):
        return self.mode=='master'

    def is_slave(self):
        return self.mode=='slave'


app_config = Config()
options = app_config

import os
os.makedirs(options.temp_dir, exist_ok=True)
os.makedirs(options.file_dir, exist_ok=True)
os.makedirs(options.image_cache_path, exist_ok=True)