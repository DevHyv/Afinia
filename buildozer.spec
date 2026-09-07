[app]
title = Afinia
package.name = afinia
package.domain = org.afinia

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# Requisitos
requirements = python3,kivy,audiostream,numpy

# Permisos
android.permissions = RECORD_AUDIO, INTERNET

# Icono
icon.filename = icon.png

orientation = portrait
fullscreen = 0

android.archs = arm64-v8a
android.minapi = 21
android.api = 33
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
