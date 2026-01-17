.. _troubleshooting:

Troubleshooting
===============

This section covers common issues you might encounter when using FeretUI and how to resolve them.

Asset Loading Errors (404)
--------------------------

**Problem**: Javascript, CSS, or Image files return a 404 Not Found error.

**Possible Causes**:
*   The static route is not correctly registered in your web framework.
*   The `base_url` parameter in `FeretUI` initialization doesn't match your web server configuration.

**Solution**:
1.  Check that you have called ``register_js``, ``register_css``, etc. correctly.
2.  Ensure your underlying framework (Flask, Django, Bottle) is configured to serve static files from the path FeretUI expects.
3.  Verify the ``base_url`` passed to ``FeretUI(...)``.

Dependency Conflicts
--------------------

**Problem**: `ImportError` or `VersionConflict` when starting the application.

**Possible Causes**:
FeretUI depends on specific versions of libraries like `WTForms`, `Jinja2`, or `BeautifulSoup4`. If your project enforces incompatible versions, it will crash.

**Solution**:
Check ``pyproject.toml`` or ``setup.py`` in your project and compare with FeretUI's requirements. Use a virtual environment to isolate dependencies.

Template Not Found
------------------

**Problem**: ``jinja2.exceptions.TemplateNotFound``

**Possible Causes**:
*   You are trying to override a template but the loader search path is incorrect.
*   The template name is typoed in your code.

**Solution**:
*   Verify the path provided to ``register_template_file``.
*   If using custom loaders, ensure the order allows finding your overrides first if that is the intention.
