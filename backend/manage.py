#!/usr/bin/env python
import os
import sys
import warnings

# Suppress requests/chardet version mismatch (chardet 7.x from reportlab
# triggers a stale check_compatibility assertion in requests).
warnings.filterwarnings("ignore", message="urllib3.*chardet.*charset_normalizer")


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smarttoll.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django. Is it installed?") from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
