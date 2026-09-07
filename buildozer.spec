[app]
title = Afinia
package.name = afinia
package.domain = org.afinia

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# Añadí "android" a los requirements. Es OBLIGATORIO para usar los permisos
requirements = python3,kivy,android

# Permisos
android.permissions = RECORD_AUDIO, INTERNET

# Icono (Asegúrate de que icon.png exista en tu repositorio, si no, bórralo o coméntalo)
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
