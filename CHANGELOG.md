# Changelog

All notable changes to the FDA Toolkit project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-08-06

### 🎉 Milestone Release - Production Deployment

This release marks a significant milestone: **FDA Toolkit is now live on PyPI** with full functionality tested and verified.

#### Added
- Complete production build and deployment pipeline
- Comprehensive package testing framework
- Version synchronization across all package files
- Distribution files ready for PyPI publishing

#### Changed
- Updated version to 0.3.0 across all package files
- Fixed version number in `__init__.py` to match `pyproject.toml`
- Improved build process with `pyproject-build`

#### Fixed
- Version mismatch between source code and package metadata
- Build configuration for isolated and non-isolated builds
- Package installation and import paths

#### Verified
- ✅ 67 production-ready functions available
- ✅ Core data cleaning functions working
- ✅ Financial parsing (currency, percentage) working
- ✅ Duplicate detection operational
- ✅ Package successfully published to PyPI
- ✅ Installation and import working in clean environments

#### Technical Details
- Built with: `pyproject-build`
- Uploaded to: PyPI using `twine`
- Tested on: Python 3.14
- Package size: 
  - Wheel: 71.8 KB
  - Source: 59.4 KB

#### Links
- PyPI Package: https://pypi.org/project/fda-toolkit/0.3.0/
- GitHub Repository: https://github.com/CoreInsightFinance/Financial-Data-Analysis-Toolkit-Workspace
- Documentation: Available on PyPI

#### Installation
```bash
pip install fda-toolkit
```

#### Quick Start
```python
import fda_toolkit
from fda_toolkit import parse_currency, find_duplicates
import pandas as pd

# Parse financial data
currencies = pd.Series(['$1,234.56', '$500.00'], dtype='object')
parsed = parse_currency(currencies)

# Detect duplicates
df = pd.DataFrame({'amount': [100, 100, 200]})
duplicates = find_duplicates(df)
```

---

## [0.2.9] - 2026-08-06

### Changed
- Updated version to 0.2.9 in pyproject.toml
- Initial PyPI upload attempt (metadata only)

### Note
- Version contained metadata mismatch, resolved in 0.3.0

---

## [0.2.8] - 2026-08-05

### Added
- Complete implementation of 67 functions across 8 categories
- Comprehensive test suite
- Full documentation in README and function references

### Categories
- Core Data Cleaning
- Feature Engineering
- Financial Domain Functions
- I/O Operations
- Data Validation
- Reporting & Profiling
- Pipeline Automation
- Utilities & Security

---

## Previous Versions

Earlier versions (0.1.0 - 0.2.7) focused on:
- Initial framework development
- Function implementation and testing
- Module organization and structure
- Documentation and examples
