#!/usr/bin/env python3

if __name__ == "__main__":
    import importlib
    from pprint import pprint
    import os
    import sys
    direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    def seed(direpas_configuration=dict()):
        print("Execute migration logic here by using direpas_configuration dictionary.")
        pprint(direpas_configuration)

    etconf=pkg.Etconf(
        enable_dev_conf=True,
        tree=dict(
            dirs=dict(
                users=dict(
                    dirs=dict(
                        info=dict()
                    ),
                    files=dict(conf=None)
                )
            ),
            files=dict({
                "settings.json": dict(),
                "configuration.json": dict(name="gabriel", job="developer"),
            })
        ),
        seed=seed,
    )
