#!/usr/bin/env python3
from pprint import pprint
import inspect
import json
import os
import re
import sys
import shutil
import traceback

class Etconf():
    def __init__(self,
        direpa_configuration=None,
        enable_dev_conf=True,
        tree=dict(),
        reset_seed=False,
        seed=None,
    ):
        self.direpas_configuration=dict()
        self.seed=seed
        self.reset_seed=reset_seed
        filenpa_caller=inspect.stack()[1].filename
        if os.path.islink(filenpa_caller):
            filenpa_caller=os.path.realpath(filenpa_caller)
        self.direpa_main=os.path.normpath(os.path.dirname(filenpa_caller))
        self.filenpa_gpm=os.path.join(self.direpa_main, "gpm.json")
        if not os.path.exists(self.filenpa_gpm):
            self._error("gpm.json file not found '{}'".format(self.filenpa_gpm))

        self.dy_gpm=None
        with open(self.filenpa_gpm, "r") as f:
            self.dy_gpm=json.load(f)

        dy_regex=dict(
            uuid4=dict(
                rule=r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-4[0-9a-fA-F]{3}\-[89ab][0-9a-fA-F]{3}\-[0-9a-fA-F]{12}$",
            ),
            version=dict(
                rule=r"^(\d+)\.\d+\.\d+$",
            ),
        )

        keys=[]
        if "alias" in self.dy_gpm:
            keys.append("alias")
            dy_regex["alias"]=dict(rule=r"^[A-Za-z][A-Za-z0-9_-]*$")
            self.pkg_alias=self.dy_gpm["alias"].lower()
        else:
            keys.append("name")
            dy_regex["name"]=dict(rule=r"^[A-Za-z][A-Za-z0-9_-]*$")
            self.pkg_alias=self.dy_gpm["name"].lower()

        keys.extend(["version", "uuid4"])

        for key in keys:
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
        
        self.pkg_major=int(dy_regex["version"]["match"][0])
        self.pkg_uuid4=self.dy_gpm["uuid4"].lower().replace("-", "")

        is_git_project=os.path.exists(os.path.join(self.direpa_main, ".git"))
        if is_git_project is True and enable_dev_conf is True:
            self.direpa_configuration=os.path.join(self.direpa_main, ".etconf", str(self.pkg_major))
        else:
            if direpa_configuration is not None:
                self.direpa_configuration=direpa_configuration
            else:
                direpa_etc=os.path.join(os.path.expanduser("~"), "fty", "etc")
                self.direpa_configuration=os.path.join(direpa_etc, self.pkg_alias[0], self.pkg_alias, self.pkg_uuid4, str(self.pkg_major))
        self._process_tree(tree, self.direpa_configuration)

    def _error(self, text, direpa_delete=None):
        print("Etconf Error: {}.".format(text))
        if direpa_delete is not None:
            print("Correct issue and remove '{}' before proceeding again.".format(direpa_delete))
        print("stack:")
        traceback.print_stack()
        sys.exit(1)

    def _process_tree(self, tree, direpa_root, dy_paths=None, key=None):
        is_root=False
        error_key=key
        if key is None:
            is_root=True
            error_key="root"
            dy_paths=dict(
                dirs=[],
                files=dict(),
            )

        if not os.path.exists(direpa_root):
            direpa_root=direpa_root.lower()
            rm_dir=None
            for direpa in dy_paths["dirs"]:
                if len(direpa) <= len(direpa_root):
                    if direpa == direpa_root[:len(direpa)]:
                        rm_dir=direpa
                        break
            if rm_dir is not None:
                dy_paths["dirs"].remove(rm_dir)
            dy_paths["dirs"].append(direpa_root)

            if not isinstance(tree, dict):
                self._error("in tree at key '{}' value type {} is not of type {}".format(error_key, type(tree), dict), self.direpa_configuration)

            for elem_type in sorted(tree):
                if elem_type in ["dirs", "files"]:
                    if not isinstance(tree[elem_type], dict):
                        self._error("in tree at key '{}' subkey '{}' is of type {} not {}".format(error_key, elem_type, type(tree[elem_type]), dict), self.direpa_configuration)

                    for elem in tree[elem_type]:
                        elem=re.sub(r"\s", "-", elem.strip()).lower()
                        path_elem=os.path.join(direpa_root, elem)
                        if elem_type in "dirs":
                            self._process_tree(tree[elem_type][elem], path_elem, dy_paths, elem)
                        elif elem_type == "files":
                            value=tree[elem_type][elem]
                            dy_paths["files"][path_elem]=value
                else:
                    self._error("in tree at key '{}' subkey '{}' is not in ['dirs', 'files']".format(error_key, elem_type), self.direpa_configuration)

        if is_root is True:
            if not os.path.exists(direpa_root):
                self.reset_seed=True
                for direpa in dy_paths["dirs"]:
                    os.makedirs(direpa, exist_ok=True)

                for filenpa, value in dy_paths["files"].items():
                    with open(filenpa, "w") as f:
                        if value is not None:
                            if type(value) in [list, dict]:
                                f.write(json.dumps(value, sort_keys=True, indent=4))
                            else:
                                f.write("{}\n".format(value))

            if self.reset_seed is True:
                if self.seed is not None:
                    if callable(self.seed):
                        direpa_pkg=os.path.dirname(self.direpa_configuration)
                        self.direpas_configuration={major:os.path.join(direpa_pkg, str(major)) for major in sorted(list(map(int, os.listdir(direpa_pkg))))}
                        self.seed(self.pkg_major, self.direpas_configuration, fun_auto_migrate=self._fun_auto_migrate)
                    else:
                        self._error("seed is not a function", self.direpa_configuration)

    def _fun_auto_migrate(self):
        all_majors=sorted(self.direpas_configuration)
        if self.pkg_major != all_majors[-1]:
            print("WARNING Etconf: Ignoring auto-migrate for package '{}' due to major version '{}' is not the latest major version '{}' from '{}'".format(
                self.pkg_alias,
                self.pkg_major,
                all_majors[-1],
                os.path.dirname(self.direpas_configuration[self.pkg_major]),
            ))
        else:
            if len(self.direpas_configuration) > 1:
                pass
                index=all_majors.index(self.pkg_major)-1
                previous_major=all_majors[index]
                print("Etconf Processing Configuration Auto-Migrations for package '{}' from major version '{}' to '{}' at '{}':".format(
                    self.pkg_alias,
                    previous_major,
                    self.pkg_major,
                    os.path.dirname(self.direpas_configuration[self.pkg_major]),
                ))

                direpa_src=self.direpas_configuration[previous_major]
                direpa_dst=self.direpas_configuration[self.pkg_major]

                migrate=True
                if len(os.listdir(direpa_dst)) > 0:
                    print("WARNING Etconf: Directory not empty '{}'".format(direpa_dst))
                    user_input=None
                    while user_input is None:
                        user_input=input("Proceed anyway? [Ynq]: ").strip()
                        if user_input == "" or user_input.lower() == "y":
                            break
                        elif user_input.lower() == "n":
                            print("Warning Etconf Configuration Auto-Migrations ignored.")
                            migrate=False
                            break
                        elif user_input.lower() == "q":
                            print("Warning Etconf Configuration Auto-Migrations canceled.")
                            sys.exit(1)
                        else:
                            print("Please type y, n, or q")
                            user_input=None

                if migrate is True:
                    self.overwrite_paths(direpa_src, direpa_dst)
                    print("SUCCESS Etconf: Configuration Auto-Migrations for package '{}' from major version '{}' to '{}' at '{}':".format(
                        self.pkg_alias,
                        previous_major,
                        self.pkg_major,
                        os.path.dirname(self.direpas_configuration[self.pkg_major]),
                    ))
                    print("You can delete previous major directory if not needed:")
                    print(direpa_src)

    def overwrite_paths(self, direpa_src, direpa_dst):
        for elem_name in os.listdir(direpa_src):
            elem_path_src=os.path.normpath(os.path.join(direpa_src, elem_name)).replace("\\", "/")
            elem_path_dst=os.path.normpath(os.path.join(direpa_dst, elem_name)).replace("\\", "/")
            if os.path.isdir(elem_path_src):
                os.makedirs(elem_path_dst, exist_ok=True)
                self.overwrite_paths(elem_path_src, elem_path_dst)
            else:
                shutil.copy(elem_path_src, direpa_dst)
