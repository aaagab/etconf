# Etconf
## Description
Package configuration generator for Python GPM packages. It allows to create a unique configuration directory for different packages with the same name, and also for packages with different versions.  
Configurarion directory follows the syntax:  
```shell
# at home directory
$HOME/fty/etc/package_first_letter/package_name/uuid4/major_version
# i.e
/home/zeus/fty/etc/p/prompt/b1a980c36e1c4072a16c81df61f2f898/3
# at git root directory
/package-path/.etconf/major_version
```
Then a dictionary of files with/without content and directories can be provided to populate the configuration directory.  

Please cf `src/samples.py` for a working example.

## Etconf Class Parameters
```python
etconf=pkg.Etconf(
    direpa_configuration=None,
    enable_dev_conf=False,
    reset_seed=False,
    tree=dict(),
    seed=None,
)
```
**direpa_configuration**: If enable_dev_conf is True and directory is a git project then configuration directory is set at git root directory. Otherwise if direpa_configuration is set then direpa configuration is going to be set there, else direpa configuration is going to be set at user home directory.
**enable_dev_conf**: Two scenarios:  
- If program is located in a git directory(development mode):
  - If enable_dev_conf is set to True then configuration directory `.etconf` is created at git root directory. 
  - If enable_dev_conf is set to False then configuration directory is created at user home directory.  
- If program is not located in a git directory:
  - If enable_dev_conf is set to True or enable_dev_conf is set to False then configuration directory is created at user home directory.  
**tree**: Provide a tree of elements dirs or files.  Etconf will create that structure into the configuration directory if this directory does not exists. Files name can take null as a value for empty file or any other value as a file content. Dict value type is going to be inserted as JSON and other value types are going to be inserted as text. Dirs name can only get an empty dict, or a dict with keywords files and/or dirs. Path for files or directories are put to lowercase and spaces are replaced with a dash.   
```python
tree=dict(
    dirs=dict(
        name=dict(
            dirs=dict(
                  name=dict()
                ),
            files=dict(name=None)
        )
    ),
    files=dict(
        name=None,
    )
)
```
**reset_seed**: This parameter is mainly for debugging, if set to True and seed function has been defined by user then each time the program executes, the seed function is called.  
**seed**: Accept a function parameter. The function must be defined by user if needed. The function is executed only once when the configuration directory is created. `seed` has two parameters:
- `pkg_major`: It is an int with the major version of the package.
- `direpas_configuration`: It is a dict with as pair:  
  - key is major version of package as integer
  - value is directory configuration path of the major version
  The use of this seed function is to migrate existing configuration data from a previous major version to the current major version. Any changes on configuration structure or parameters is considered a major change in the software (aka breaking change). That is why only major versions are targeted for package configuration.  
i.e.:  
```python
{
  2: '/home/zeus/fty/etc/p/prompt/b1a980c36e1c4072a16c81df61f2f898/2'
  3: '/home/zeus/fty/etc/p/prompt/b1a980c36e1c4072a16c81df61f2f898/3'
}
```
- `fun_auto_migrate`: This parameter is a function that can be executed in order to migrate data from a previous major version to the current major version. Data are basically copied from source to destination. The function is ignored if:  
  -  There is only one major version in the direpa configuration directory. 
  -  There is multiple major versions in the direpa configuration directory and the current major versions is not the highest one (error).  
  Also if data already exists in current major version configuration directory, then user is prompted to allow the data to be overwritten.  
  
## Etconf Class Parameters
**self.dy_gpm**: It returns a dictionary with package gpm.json content.  
**self.direpa_bin**: It returns the path of the bin package.  
**self.direpa_configuration**: It returns the path of the package configuration.  
**self.pkg_major**: It returns the package major version.  
**self.pkg_name**: It returns the package name.  
**self.pkg_uuid4**: It returns the pacakge UUID4 lowercased with dash removed.  

 