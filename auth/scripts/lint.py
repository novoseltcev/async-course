import subprocess

from black import main as black
from mypy import main as mypy

from .const import modules


def main() -> None:
    print('\nRuff:')
    subprocess.run(args=['ruff', *modules])

    print('\nMypy:')
    mypy.main(args=[*modules], clean_exit=True)

    print('\nBlack:')
    black.main([*modules, '--check'], standalone_mode=False)


if __name__ == '__main__':
    main()
