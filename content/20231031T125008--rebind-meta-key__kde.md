---
title: Rebind the Meta Key
date: 2023-10-31T12:50:08+00:00
tags:
  - linux
  - kde
identifier: 20231031T125008
---

# Rebind the Meta Key

Using D-Bus it's possible to query the set of available shortcut names

```
qdbus org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.shortcutNames | sort
```

The ``kwriteconfig5`` command can then be used to edit the ``kwinrc`` file to remap the key binding

```
kwriteconfig5 --file ~/.config/kwinrc --group ModifierOnlyShortcuts --key Meta "org.kde.kglobalaccel,/component/kwin,org.kde.kglobalaccel.Component,invokeShortcut,<shortcut-name>"
```

Finally, poke KWin via D-Bus to reload the config

```
qdbus org.kde.KWin /KWin reconfigure
```

[Windows/Meta Key](https://userbase.kde.org/Plasma/Tips#Windows/Meta_Key)
