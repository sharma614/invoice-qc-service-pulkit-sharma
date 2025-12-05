from setuptools import setup, find_packages

setup(
    name="invoice-qc-service",
    version="1.0.0",
    description="Invoice QC service: extract, validate, report on invoices from PDFs",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pdfplumber>=0.5.28",
        "PyPDF2>=3.0.0",
        "fastapi>=0.95.0",
        "uvicorn[standard]>=0.22.0",
        "pydantic>=1.10.7",
    ],
    entry_points={
        "console_scripts": [
            "invoice-qc=invoice_qc.cli:main",
        ]
    }
)
