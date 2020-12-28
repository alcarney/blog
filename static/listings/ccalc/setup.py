from setuptools import setup, Extension

ccalcmod = Extension("_ccalc", sources=['ccalcmodule.c'], language='c')

setup(
    name="ccalc",
    version="1.0.0",
    description="A simple calculator implemented in C",
    author="Alex Carney",
    author_email="alcarneyme@gmail.com",
    packages = ['ccalc'],
    ext_modules=[ccalcmod]
)
