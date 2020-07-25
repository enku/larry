from setuptools import setup


def readme():
    with open("README.md") as fp:
        return fp.read()


setup(
    name="larry",
    version="1.6.1",
    url="https://github.com/enku/larry",
    license="MIT",
    description="Colorify your desktop with Larry the Cow",
    long_description=readme(),
    author="Albert Hopkins",
    author_email="marduk@letterboxes.org",
    packages=["larry", "larry.plugins"],
    zip_safe=True,
    install_requires=["aionotify", "dbus-python"],
    entry_points={
        "console_scripts": {"larry = larry:main"},
        "larry.plugins": {
            "command = larry.plugins.command:plugin",
            "gnome_background = larry.plugins.background:plugin",
            "gnome_shell = larry.plugins.gnome_shell:plugin",
            "gnome_terminal = larry.plugins.gnome_terminal:plugin",
            "gtk = larry.plugins.gtk:plugin",
            "vim = larry.plugins.vim:plugin",
        },
        "larry.algos": {
            "gradient = larry.algos:gradient_algo",
            "inverse = larry.algos:inverse_algo",
            "luminocity = larry.algos:luminocity_algo",
            "zipgradient = larry.algos:zipgradient_algo",
        }
    },
    include_package_data=True,
)
