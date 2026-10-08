[app]

# (str) Title of your application
title = BGMI Match Freeze Pro

# (str) Package name
package.name = bgmifreeze

# (str) Package domain (needed for android/ios packaging)
package.domain = org.bgmi.freeze

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,html

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,customtkinter,httpx,psutil

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# comma separated permissions e.g. permissions = INTERNET,ACCESS_NETWORK_STATE
permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (list) List of Java .jar files to add to the libs so that your custom classes can be referenced
# android.add_libs_sqlite3 = libs/arm64-v8a/libsqlite3.so

# (list) Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable AndroidX support. Necessary for modern Android SDKs.
android.enable_androidx = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = error, 1 = warning)
warn_on_root = 1
