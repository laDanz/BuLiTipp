#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BuLiTipp.settings")
    import BuLiTipp.settings
    from BuLiTippApp.models import Tabelle
    
    Tabelle().refresh()
