

import os
from os.path import isdir, join 

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

FRAMEWORK_DIR = env.PioPlatform().get_package_dir("framework-arduino-k210")
assert FRAMEWORK_DIR and isdir(FRAMEWORK_DIR)
SDK_DIR = join(FRAMEWORK_DIR, "cores", "k210", "k210-sdk")
RT_DIR = join(FRAMEWORK_DIR, "cores", "k210", "rt-thread")

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
        join(SDK_DIR, "bsp"),
        join(SDK_DIR, "drivers"),
        join(SDK_DIR, "drivers", "include"),
        join(SDK_DIR, "nncase"),
        join(SDK_DIR, "nncase", "include"),
        join(SDK_DIR, "nncase", "runtime"),
        join(SDK_DIR, "third_party", "xtl", "include", "xtl"),
        join(RT_DIR, "bsp"),
        join(RT_DIR, "include", "CPU"),
        join(RT_DIR, "include", "DeviceDrivers"),
        join(RT_DIR, "include", "DeviceDrivers", "drivers"),
        join(RT_DIR, "include", "DeviceDrivers", "ipc"),
        join(RT_DIR, "include", "bsp"),
        join(RT_DIR, "include", "kernel"),
        join(RT_DIR, "include", "libc", "common"),
        join(RT_DIR, "include", "libc", "cplusplus"),
        join(RT_DIR, "include", "libc", "newlib"),
        join(RT_DIR, "lib"),
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