#!/usr/bin/env python3
from pprint import pprint
import inspect
import json
import os
import re
import sys
import traceback

class Etconf():
    def __init__(self,
        enable_dev_conf=True,
        tree=dict(),
        seed=None,
    ):
        self.seed=seed
        self.direpa_src=os.path.normpath(os.path.dirname(inspect.stack()[1].filename))
        self.filenpa_gpm=os.path.join(self.direpa_src, "gpm.json")
        if not os.path.exists(self.filenpa_gpm):
            self._error("gpm.json file not found '{}'".format(self.filenpa_gpm))

        self.dy_gpm=None
        with open(self.filenpa_gpm, "r") as f:
            self.dy_gpm=json.load(f)

        dy_regex=dict(
            name=dict(
                rule=r"^[A-Za-z][A-Za-z0-9_-]*$",
            ),
            uuid4=dict(
                rule=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-4[0-9a-fA-F]{3}\-[89ab][0-9a-fA-F]{3}\-[0-9a-fA-F]{12}$",
            ),
            version=dict(
                rule=r"^(\d+)\.\d+\.\d+$",
            ),
        )

        for key in ["name", "version" , "uuid4"]:
            if not key in self.dy_gpm:
                self._error("in gpm.json '{}' not found".format(key))
            value=self.dy_gpm[key].strip()
            if value is None or value == "" :
                self._error("in gpm.json '{}' value can't be null".format(key))
            reg=re.match(dy_regex[key]["rule"], value)
            if reg:
                dy_regex[key]["match"]=list(reg.groups())
            else:
                self._error("in gpm.json '{}' with value '{}' does not match regex '{}'".format(key, value, dy_regex[key]["rule"]))
        
        self.pkg_major=dy_regex["version"]["match"][0]
        self.pkg_uuid4=self.dy_gpm["uuid4"].lower().replace("-", "")
        self.pkg_name=self.dy_gpm["name"].lower()

        is_git_project=os.path.exists(os.path.join(self.direpa_src, ".git"))
        if is_git_project is True and enable_dev_conf is True:
            self.direpa_conf=os.path.join(self.direpa_src, ".etconf", self.pkg_major)
        else:
            direpa_etc=os.path.join(os.path.expanduser("~"), "fty", "etc")
            self.direpa_conf=os.path.join(direpa_etc, self.pkg_name[0], self.pkg_name, self.pkg_uuid4, self.pkg_major)

        self._process_tree(tree, self.direpa_conf)

    def _error(self, text, direpa_delete=None):
        print("Etconf Error: {}.".format(text))
        if direpa_delete is not None:
            print("Correct issue and remove '{}' before proceeding again.".format(direpa_delete))
        print("stack:")
        traceback.print_stack()
        sys.exit(1)

    def _process_tree(self, tree, direpa_root, key=None):
        is_root=False
        error_key=key
        if key is None:
            is_root=True
            error_key="root"

        conf_generated=False
        if not os.path.exists(direpa_root):
            conf_generated=True
            direpa_root=direpa_root.lower()
            os.makedirs(direpa_root, exist_ok=True)

            if not isinstance(tree, dict):
                self._error("in tree at key '{}' value type {} is not of type {}".format(error_key, type(tree), dict), self.direpa_conf)

            for elem_type in sorted(tree):
                if elem_type in ["dirs", "files"]:
                    if not isinstance(tree[elem_type], dict):
                        self._error("in tree at key '{}' subkey '{}' is of type {} not {}".format(error_key, elem_type, type(tree[elem_type]), dict), self.direpa_conf)

                    for elem in tree[elem_type]:
                        elem=re.sub(r"\s", "-", elem.strip()).lower()
                        path_elem=os.path.join(direpa_root, elem)
                        if elem_type in "dirs":
                            self._process_tree(tree[elem_type][elem], path_elem, elem)
                        elif elem_type == "files":
                            value=tree[elem_type][elem]
                            with open(path_elem, "w") as f:
                                if value is not None:
                                    if isinstance(value, dict):
                                        f.write(json.dumps(value, sort_keys=True, indent=4))
                                    else:
                                        f.write("{}\n".format(value))
                else:
                    self._error("in tree at key '{}' subkey '{}' is not in ['dirs', 'files']".format(error_key, elem), self.direpa_conf)

        if is_root is True and conf_generated is True:
            if self.seed is not None:
                if callable(self.seed):
                    direpa_pkg=os.path.dirname(self.direpa_conf)
                    direpa_pkgs={major:os.path.join(direpa_pkg, str(major)) for major in sorted(list(map(int, os.listdir(direpa_pkg))))}
                    self.seed(direpa_pkgs)
                else:
                    self._error("seed is not a function", self.direpa_conf)

