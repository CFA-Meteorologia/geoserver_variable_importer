import yaml
import pathlib
from os import path
from dict_deep import deep_get

with open(path.join(pathlib.Path(__file__).parent.absolute(), "config.yml"), 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)


def get_config(prop_path, default_value=None):
    v = deep_get(cfg, prop_path)

    if v is None:
        return default_value
    return v
