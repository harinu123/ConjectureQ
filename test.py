
2025-06-15 23:05:22.874 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-06-15 23:05:22.974 503 GET /script-health-check (127.0.0.1) 104.90ms

2025-06-15 23:05:27.880 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 553, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 46, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/conjectureq/test.py", line 218

        result = oauth2.authorize_button(

    ^

SyntaxError: invalid non-printable character U+00A0
