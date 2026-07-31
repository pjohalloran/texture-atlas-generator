import os
import sys

SRC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)
