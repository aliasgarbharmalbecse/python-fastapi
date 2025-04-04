import os
import pkgutil
import importlib

# Automatically import all modules inside the `models` directory
package_dir = os.path.dirname(__file__)

for _, module_name, _ in pkgutil.iter_modules([package_dir]):
    importlib.import_module(f"models.{module_name}")