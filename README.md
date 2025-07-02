# Briefcase P4A Backend

**Python-for-Android backend for Briefcase**

## Features

- Direct P4A Integration: Uses python-for-android directly within Briefcase
- Android Support: Build debug and release APKs with Android functionality
- Briefcase SDK Management: Leverages Briefcase's Android SDK management system
- Dynamic NDK Detection: Automatically detects and uses installed NDK versions
- Python 3.13 Compatibility: Automatic version detection with conditional pyjnius handling
- Fast Builds: Reuses P4A distributions for faster subsequent builds
- Kivy Support: Support for Kivy applications and widgets

## Installation

```bash
pip install git+https://github.com/pyCino/briefcase-p4a-backend.git
```

## Quick Start

1. **Create a new Briefcase project:**
   ```bash
   briefcase new -t https://github.com/pyCino/briefcase-p4a-template.git --template-branch main
   ```

2. **Build Android APK using P4A:**
   ```bash
   briefcase create android p4a
   briefcase build android p4a
   ```

3. **Package release APK:**
   ```bash
   briefcase package android p4a
   ```

4. **Run on device/emulator:**
   ```bash
   briefcase run android p4a
   ```

## Prerequisites

- Python 3.8+ (including Python 3.13)
- Briefcase 0.3.23+
- Android SDK (automatically managed by Briefcase)
- Android NDK (install via `briefcase create android` or Android SDK Manager)
- Python-for-Android 2024.1.21+
- Cython 0.29.0+

### Python 3.13 Compatibility

This backend automatically detects your Python version and handles pyjnius compatibility:

**For Python 3.13+:**
1. Automatically uses `git+https://github.com/kivy/pyjnius.git` (master branch)
2. Warns about potential conflicts with existing pyjnius installations
3. Uses master branch pyjnius recipe for APK builds

**For Python 3.8-3.12:**
1. Uses stable `pyjnius>=1.4.1` release
2. Uses standard pyjnius recipe for APK builds

**Compatibility Checking:**
- Detects existing pyjnius installations and versions  
- Warns if your environment has incompatible pyjnius for Python 3.13+
- Automatically configures correct requirements in generated projects

## How It Works

This backend provides direct Python-for-Android integration into Briefcase's build pipeline:

1. **Template Generation**: Creates P4A-compatible project structure using cookiecutter
2. **SDK Configuration**: Automatically configures Android SDK/NDK paths
3. **P4A Build**: Executes P4A commands with arguments and environment
4. **APK Packaging**: Handles APK location and naming conventions
5. **Distribution Management**: Reuses P4A distributions for faster builds

## Configuration

The backend automatically registers when installed. No additional configuration needed.

**Entry Point:**
```toml
[project.entry-points."briefcase.formats.android"]
p4a = "briefcase_p4a_backend"
```

**Project Structure:**
```
your-project/
├── pyproject.toml
├── src/
│   └── yourapp/
│       ├── __init__.py
│       ├── __main__.py
│       └── main.py
└── build/
    └── yourapp/
        └── android/
            └── yourapp/
                ├── src/
                │   ├── main.py          # P4A entry point
                │   └── yourapp/         # Your app code
                └── *.apk                # Generated APKs
```

## Troubleshooting

### PyJNIus Build Errors (Python 3.13)
**Solution**: Automatically handled by version detection.

```bash
# Manual fix if needed:
pip install git+https://github.com/kivy/pyjnius.git
```

### SDK/NDK Not Found
**Solution**: Ensure Briefcase has installed Android SDK:
```bash
briefcase create android p4a  # This installs SDK automatically
```

### Main.py Not Found Error
**Solution**: The backend automatically creates the required `main.py` entry point. If you see this error, try:
```bash
briefcase clean android p4a
briefcase create android p4a
briefcase build android p4a
```

### Template Variables Missing
**Solution**: Check `pyproject.toml` for required fields:
```toml
[tool.briefcase.app.yourapp]
formal_name = "Your App Name"
bundle = "com.example"
version = "0.1.0"
```

### Debug Commands
```bash
# Verbose output
briefcase build android p4a -v

# Clean build
briefcase clean android p4a
briefcase build android p4a

# Test backend installation
python -c "import briefcase_p4a_backend; print('Backend installed successfully')"

# Check P4A installation
p4a --version
```

## Development

```bash
# Clone repository
git clone https://github.com/pyCino/briefcase-p4a-backend.git
cd briefcase-p4a-backend

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
black briefcase_p4a_backend/
flake8 briefcase_p4a_backend/
mypy briefcase_p4a_backend/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Related Projects

- [Briefcase](https://github.com/beeware/briefcase) - Cross-platform Python app packaging
- [Python-for-Android](https://github.com/kivy/python-for-android) - Android build system for Python

- [PyJNIus](https://github.com/kivy/pyjnius) - Python-Java bridge

## Contributing

Contributions are welcome. Please submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Author

**Al pyCino** - [thealpycino@gmail.com](mailto:thealpycino@gmail.com)

---

*Making the world more beautiful, one APK at a time* 