from hydra import compose, initialize, core
from omegaconf import DictConfig

initialize(config_path="../conf", job_name="test", version_base=None)

def load_config() -> DictConfig:    
    cfg = compose(config_name="config")
    core.global_hydra.GlobalHydra.instance().clear()
    
    return cfg


if __name__ == '__main__':
    print(load_config())

