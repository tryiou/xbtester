import logging

formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s',
                              "%Y-%m-%d %H:%M:%S")  # '%(asctime)s %(levelname)s %(message)s')


# formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s","%Y-%m-%d %H:%M:%S")
def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    # handler.setFormatter()
    log_handle = logging.getLogger(name)
    log_handle.setLevel(level)
    log_handle.addHandler(handler)
    return log_handle
