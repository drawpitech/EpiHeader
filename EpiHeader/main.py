import sys
from pathlib import Path
from enum import Enum, auto

class Args:
    def __init__(self, args: list[str]):
        self.__args: list[str] = args.copy()
        self.__search_help()
        self.project_name: str = self.__set_project_name()
        self.files: list[Path] = self.__set_files()

    def __search_help(self) -> None:
        if "--help" not in self.__args:
            return
        usage()
        sys.exit(0)

    def __set_project_name(self) -> str:
        if "--name" in self.__args:
            index = self.__args.index("--name")
            if index + 1 == len(self.__args):
                usage()
                sys.exit(1)
            name = self.__args[index + 1]
            self.__args.pop(index + 1)
            self.__args.pop(index)
            return name
        name = ""
        while not name:
            try:
                name = input("Project name: ")
            except KeyboardInterrupt:
                print("Exit")
                sys.exit(1)
        return name

    def __set_files(self) -> list[Path]:
        files: list[Path] = []
        for arg in self.__args:
            f = Path(arg)
            if f.is_file():
                files.append(f)
                continue
            if f.is_dir():
                self.__add_folder(f, files)
                continue
            print(f"File {arg} does not exist")
            sys.exit(1)
        if not files:
            self.__add_folder(Path("."), files)
        return files

    def __add_folder(self, folder: Path, files: list[Path]):
        for f in folder.iterdir():
            if f.is_file():
                files.append(f)
            elif f.is_dir():
                self.__add_folder(f, files)


def usage():
    print(
        "Usage: epi-header [options] files...\n"
        "Options:\n"
        " --help\t\t\tShow this message\n"
        " --name <name>\t\tSet project name"
    )


class FileType(Enum):
    MAKEFILE = auto()
    SOURCE = auto()
    SKIPPED = auto()


def get_file_type(file: Path) -> FileType:
    if file.suffix[1:] in { "h", "c" }:
        return FileType.SOURCE

    if file.suffix[1:] in { "mk", "make" } or file.name == "Makefile":
        return FileType.MAKEFILE

    return FileType.SKIPPED


def _fix_make_headers(
    file: Path, lines: list[str], project_name: str
) -> None:
    if len(lines) < 5 or not lines[2].startswith("## "):
        print(f"File {file} has an invalid header")
        return

    lines[2] = f"## {project_name}\n"
    lines[4] = f"## {file.name.split('.')[0]}\n"


def _fix_source_headers(
    file: Path, lines: list[str], project_name: str
) -> None:
    if len(lines) < 5 or not lines[2].startswith("** "):
        print(f"File {file} has an invalid header")
        return

    lines[2] = f"** {project_name}\n"
    filename = file.name.split('.')[0]

    if filename.startswith("test_"):
        filename = f"tests for {filename[5:]}"
    lines[4] = f"** {filename}\n"


def fix_header(file: Path, project_name: str) -> None:
    filetype = get_file_type(file)
    if (filetype == FileType.SKIPPED):
        return

    with open(file, "r") as f:
        lines = f.readlines()

    if filetype == FileType.SOURCE:
        _fix_source_headers(file, lines, project_name)
    elif filetype == FileType.MAKEFILE:
        _fix_make_headers(file, lines, project_name)
    else:
        raise ValueError("Unexpected FileType")

    with open(file, "w") as f:
        f.writelines(lines)


def main():
    args = Args(sys.argv[1:])
    for file in args.files:
        fix_header(file, args.project_name)


if __name__ == "__main__":
    main()
