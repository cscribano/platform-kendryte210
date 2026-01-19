

import os
from os.path import isdir, join 

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

FRAMEWORK_DIR = env.PioPlatform().get_package_dir("framework-arduino-k210")
assert FRAMEWORK_DIR and isdir(FRAMEWORK_DIR)
SDK_DIR = join(FRAMEWORK_DIR, "cores", "k210", "k210-sdk")

env.SConscript("_bare.py", exports="env")

env.Append(

    CCFLAGS = [
        "-Wno-error=unused-const-variable",
        "-Wno-error=narrowing",
        "-Wno-error=unused-value"
    ],

    CPPDEFINES = [
        ("ARDUINO", 10805),
        ("ARDUINO_VARIANT", '\\"%s\\"' % env.BoardConfig().get("build.variant").replace('"', "")),
        ("ARDUINO_BOARD", '\\"%s\\"' % env.BoardConfig().get("build.board_def").replace('"', "")),
        ("NNCASE_TARGET", "k210"),
        "TCB_SPAN_NO_EXCEPTIONS",
        "TCB_SPAN_NO_CONTRACT_CHECKING"
    ],

    LINKFLAGS = [
        "-Wl,--start-group",
        "-lc",
        "-lgcc",
        "-lm",
        "-Wl,--end-group"
    ],

    CPPPATH = [
        join(FRAMEWORK_DIR, "cores", "k210"),
        join(FRAMEWORK_DIR, "cores", "k210", "k210-hal"),
        join(FRAMEWORK_DIR, "cores", "k210", "k210-hal", "include"),
        join(SDK_DIR, "lib", "bsp"),
        join(SDK_DIR, "lib", "bsp", "include"),
        join(SDK_DIR, "lib", "drivers"),
        join(SDK_DIR, "lib", "drivers", "include"),
        join(SDK_DIR, "lib", "freertos"),
        join(SDK_DIR, "lib", "freertos", "include"),
        join(SDK_DIR, "lib", "freertos", "portable"),
        join(SDK_DIR, "lib", "freertos", "conf"),
        join(SDK_DIR, "lib", "utils", "include"),
        join(SDK_DIR, "lib", "nncase"),
        join(SDK_DIR, "lib", "nncase", "include"),
        join(SDK_DIR, "lib", "nncase", "runtime"),
        join(SDK_DIR, "third_party", "xtl", "include")
    ],

    LIBPATH = [

    ],
    
    LIBS = [ 
        "c", "gcc", "m"
    ],

    LIBSOURCE_DIRS=[
        join(FRAMEWORK_DIR, "libraries")
    ],
    
)

if not env.BoardConfig().get("build.ldscript", ""):
    env.Replace(LDSCRIPT_PATH=join(SDK_DIR, "lds", "kendryte.ld"))

#
# Target: Build Core Library
#

libs = []

if "build.variant" in env.BoardConfig():
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "variants",
                 env.BoardConfig().get("build.variant"))
        ]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinok210Variant"),
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"))
    ))

envsafe = env.Clone()

libs.append(envsafe.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduinok210"),
    join(FRAMEWORK_DIR, "cores", "k210"),
    ["+<*>", "-<.git%s>" % os.sep, "-<.svn%s>" % os.sep, "-<kendryte-standalone-sdk/src/hello_world%s>" % os.sep]
))


env.Prepend(LIBS=libs)
