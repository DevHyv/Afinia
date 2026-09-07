[app]
title = Afinia
package.name = afinia
package.domain = org.afinia

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# Requerimientos: audiostream para captura de audio, numpy para procesamiento
requirements = python3,kivy,numpy,audiostream

# Permisos para acceder al micrófono de Android
android.permissions = RECORD_AUDIO, INTERNET

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
