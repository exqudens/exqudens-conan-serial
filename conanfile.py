import logging
from pathlib import Path
from conans import ConanFile, tools


required_conan_version = ">=1.50.0"


class ConanConfiguration(ConanFile):
    settings = "arch", "os", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    def set_name(self):
        try:
            self.name = Path(__file__).parent.joinpath('name-version.txt').read_text().split(':')[0].strip().lower()
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e

    def set_version(self):
        try:
            self.version = Path(__file__).parent.joinpath('name-version.txt').read_text().split(':')[1].strip()
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e

    def package_info(self):
        try:
            self.cpp_info.names["cmake_find_package"] = self.name
            self.cpp_info.libs = tools.collect_libs(self)
        except Exception as e:
            logging.error(e, exc_info=True)
            raise e


if __name__ == "__main__":
    pass
