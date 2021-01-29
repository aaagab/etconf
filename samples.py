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

    def seed(pkg_major, direpas_configuration=dict(), fun_auto_migrate=None):
        print("Execute migration logic here by using direpas_configuration dictionary.")
        pprint(direpas_configuration)
        fun_auto_migrate()

    etconf=pkg.Etconf(
        direpa_configuration=None,
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
        reset_seed=False,
        # reset_seed=True,
        seed=seed,
    )

    print(etconf.dy_gpm)
    print(etconf.direpa_configuration)
    print(etconf.direpas_configuration)
    print(etconf.pkg_major)
    print(etconf.pkg_name)
    print(etconf.pkg_uuid4)