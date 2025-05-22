import yaml

def load_config(config_path):
    with open(config_path) as cfgfile:
        config = yaml.safe_load(cfgfile)
        wrap_config_keys(config)
        return config

def wrap_config_keys(config):
    for src in config['sources']:
        current = config['sources'][src]
        array_wrap_key(current, 'csvfile')

    if 'schemas' in config:
        for schema in config['schemas']:
            current = config['schemas'][schema]
            array_wrap_key(current, 'sources')
            array_wrap_key(current, 'each_row')

    array_wrap_key(config['output'], 'schemas')

def array_wrap_key(config, key):
    if key in config and type(config[key]) == str:
        config[key] = [ config[key] ]
