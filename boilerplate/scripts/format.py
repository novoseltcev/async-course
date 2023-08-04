import subprocess

from black import main as black

from .const import modules


def main() -> None:
    print('\nRuff:')
    subprocess.run(args=['ruff', *modules, '--fix'])

    print('\nBlack:')
    black.main([*modules])


if __name__ == '__main__':
    main()
