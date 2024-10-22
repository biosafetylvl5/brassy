import logging

try:
    import importlib.metadata

    __version__ = importlib.metadata.version(__package__ or __name__)
except ModuleNotFoundError:
    try:
        import importlib_metadata

        __version__ = importlib_metadata.version(__package__ or __name__)
    except ModuleNotFoundError:
        logging.debug(
            "Could not set __version__ because importlib.metadata is not available."
            + "If running python 3.7, installing importlib-metadata will fix this issue"
        )
