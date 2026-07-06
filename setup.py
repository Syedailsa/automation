from setuptools import setup, find_packages

setup(
    name="notebooklm-playwright",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.49.1",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.3",
        "pyyaml>=6.0.1",
        "cryptography>=41.0.7",
        "aiofiles>=23.2.1",
        "rich>=13.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
        ],
    },
    python_requires=">=3.10",
    author="NotebookLM Agent",
    description="Playwright automation agent for Google NotebookLM",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
