Installing npm packages globally without root
=============================================

1. Create a folder for global packages to be install into

   .. code-block:: console

      $ mdkir "${HOME}/.npm-packages"

2. Tell ``npm`` to use this folder

   .. code-block:: console

      $ npm config set prefix "${HOME}/.npm-packages"

3. Add the corresponding ``${HOME}/.npm-packages/bin`` folder to your ``PATH``