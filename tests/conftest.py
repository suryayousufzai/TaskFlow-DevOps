# conftest.py
# pytest looks for this file automatically before running any tests
# i need this so python can find the app/ folder when running tests from the tests/ directory
# without it you'd get "ModuleNotFoundError: No module named 'app'"

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
