"""
Patches the installed ryu package for compatibility with modern
oslo.config/oslo.i18n and eventlet releases.

Run this after installing ryu (and its dependencies) in the current
Python environment: `python scripts/patch_ryu.py`
"""
import os
import sysconfig


def create_oslo_shim():
    """
    Modern oslo.config/oslo.i18n wheels no longer ship the legacy oslo.*
    namespace package that ryu's code imports from (e.g. `from oslo.config
    import cfg`). This creates a small shim package so those imports work.
    """
    site_packages = sysconfig.get_paths()['purelib']
    oslo_dir = os.path.join(site_packages, 'oslo')
    os.makedirs(oslo_dir, exist_ok=True)

    with open(os.path.join(oslo_dir, '__init__.py'), 'w') as f:
        f.write(
            "import sys\n"
            "import oslo_config\n"
            "import oslo_config.cfg\n"
            "import oslo_i18n\n"
            "sys.modules['oslo.config'] = oslo_config\n"
            "sys.modules['oslo.i18n'] = oslo_i18n\n"
            "config = oslo_config\n"
            "i18n = oslo_i18n\n"
        )
    print(f"Created oslo namespace shim at {oslo_dir}")


def patch_ryu_wsgi():
    """
    ryu/app/wsgi.py references an ALREADY_HANDLED constant that newer
    eventlet versions removed. This strips that reference out.
    """
    site_packages = sysconfig.get_paths()['purelib']
    wsgi_path = os.path.join(site_packages, 'ryu', 'app', 'wsgi.py')

    with open(wsgi_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    skip_next = 0
    for line in lines:
        if skip_next > 0:
            skip_next -= 1
            continue
        if 'from eventlet.wsgi import ALREADY_HANDLED' in line:
            skip_next = 1
            continue
        if 'return self._ALREADY_HANDLED' in line:
            new_lines.append(line.replace('return self._ALREADY_HANDLED', 'return []'))
            continue
        new_lines.append(line)

    with open(wsgi_path, 'w') as f:
        f.writelines(new_lines)
    print(f"Patched {wsgi_path}")


if __name__ == "__main__":
    create_oslo_shim()
    patch_ryu_wsgi()