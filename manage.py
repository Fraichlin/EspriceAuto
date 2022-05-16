#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import pandas as pd
from sklearn.base import BaseEstimator

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esprice.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    class NoTransformer(BaseEstimator):
        # Passes through data without any change and is compatible with ColumnTransformer class
        def fit(self, X, y=None):
            return self

        def transform(self, X):
            assert isinstance(X, pd.DataFrame)
            return X
    main()

