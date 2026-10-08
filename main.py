if __name__ == '__main__':
    import os
    import sys

    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(os.path.abspath(sys.executable)))

    from config import config
    from ok import OK

    config = config
    ok = OK(config)
    ok.start()
