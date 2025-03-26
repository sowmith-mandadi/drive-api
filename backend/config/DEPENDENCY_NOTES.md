# Python 3.13 Dependency Notes

## Compatibility Issues

Some packages in the original requirements.txt were not compatible with Python 3.13. The main issues were:

1. **Pillow 9.5.0** - The old dependency required by python-pptx 0.6.22 is not compatible with Python 3.13
2. **numpy 1.26.1** - Not compatible with Python 3.13
3. **Various Google Cloud packages** - Required updates for Python 3.13 compatibility

## Solutions

The following changes were made to fix these issues:

1. Updated Pillow to version 11.0.0+ which is compatible with Python 3.13
2. Updated python-pptx to version 1.0.2+ which works with the newer Pillow
3. Updated numpy to version 2.2.4+ for Python 3.13 compatibility
4. Updated Google Cloud dependencies to compatible versions

## Running the Application

To run the application:

```bash
# Activate the virtual environment
source venv/bin/activate

# Make sure all dependencies are installed
pip install -r requirements.txt

# Run the application (on port 3001 since 3000 might be in use)
PORT=3001 python run.py
```

## Reinstalling Dependencies

If you need to reinstall all dependencies, you can use the `fix_dependencies.sh` script:

```bash
# Make it executable if not already
chmod +x fix_dependencies.sh

# Run the script
./fix_dependencies.sh
```

This script installs all dependencies in the correct order, ensuring compatibility with Python 3.13. 