

import os
from os.path import isdir, join 
import glob

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

FRAMEWORK_DIR = env.PioPlatform().get_package_dir("framework-arduino-k210")
if not FRAMEWORK_DIR:
    raise Exception("framework-arduino-k210 package not found")

CORES_PATH   = join(FRAMEWORK_DIR, "cores", "k210")
SDK_PATH     = join(CORES_PATH, "k210-sdk")
RTT_PATH     = join(CORES_PATH, "rt-thread")
INCLUDE_PATH = join(RTT_PATH, "include")

linker_script = join(RTT_PATH, "lds", "link.ld")
if not os.path.isfile(linker_script):
    raise Exception("Linker script not found: " + linker_script)

#env.SConscript("_bare.py", exports="env")

env.Append(

    CPPDEFINES = [

        "CONFIG_LOG_ENABLE",  #debug flags
        ("CONFIG_LOG_LEVEL", "LOG_INFO"),
        ("DEBUG", "1"),
        ("ARCH", "K210"),
        ("F_CPU", "$BOARD_F_CPU"),

        ("ARDUINO", 10805),
        ("ARDUINO_VARIANT", '\\"%s\\"' % env.BoardConfig().get("build.variant").replace('"', "")),
        ("ARDUINO_BOARD", '\\"%s\\"' % env.BoardConfig().get("build.board_def").replace('"', "")),
        ("NNCASE_TARGET", "k210"),
        "TCB_SPAN_NO_EXCEPTIONS",
        "TCB_SPAN_NO_CONTRACT_CHECKING",

        # compiler.lib.flags
        "__riscv64",
        "__RTTHREAD__",
        "RT_USING_LIBC",
        "RT_USING_NEWLIBC",
        ("_POSIX_C_SOURCE", 1),
        ("iomem_free", "free"),
        ("iomem_malloc", "malloc"),

        # compiler.build.flags
        "KENDRYTE_K210",
        ("ONLY_KMODEL_V3", 1)
    ],

    LINKFLAGS = [
        f"-T{linker_script}",
        "-mcmodel=medany",
        "-march=rv64imafc",
        "-mabi=lp64f",
        "-fsingle-precision-constant",
        "-nostartfiles",
        "-static",
        "-Wl,--gc-sections",
        "-u", "vfs_include_syscalls_impl",
    ],

    CPPPATH = [
        env.Dir(".").abspath,
        CORES_PATH,
        join(CORES_PATH, "k210-hal"),
        join(SDK_PATH, "bsp"),
        join(SDK_PATH, "drivers"),
        join(SDK_PATH, "nncase", "include"),
        join(SDK_PATH, "third_party", "xtl", "include"),
        join(CORES_PATH, "components", "include"),
        join(RTT_PATH, "lib"),
        INCLUDE_PATH,
        join(INCLUDE_PATH, "bsp"),
        join(INCLUDE_PATH, "kernel"),
        # IMPORTANT:
        # The next four "libc/*" include dirs are the ones that often break newlib
        # headers (clock_t, etc.) by shadowing the toolchain's sys/types.h.
        # We'll *not* add them as -I by default.
        join(INCLUDE_PATH, "libc", "common"),
        join(INCLUDE_PATH, "libc", "cplusplus"),
        join(INCLUDE_PATH, "libc", "newlib"),
        join(INCLUDE_PATH, "libc", "posix"),
        join(INCLUDE_PATH, "DeviceDrivers"),
        join(INCLUDE_PATH, "CPU"),
    ],

    LIBPATH = [
        join(RTT_PATH, "lib")
    ],
    
    LIBS = [ 
        "c", "gcc", "m"
    ],

    LIBSOURCE_DIRS=[
        join(FRAMEWORK_DIR, "libraries")
    ],
    
)

rtt_lib_dir = join(RTT_PATH, "lib")
archives = sorted(glob.glob(join(rtt_lib_dir, "*.a")))

# Put archives at the END of the link line (LIBS), and wrap in a group
# so ld can iterate to resolve cross-archive symbols like entry().
env.Append(LINKFLAGS=["-Wl,--start-group"])
env.Append(LINKFLAGS=[env.File(a) for a in archives])
env.Append(LINKFLAGS=["-Wl,--end-group"])


# ------------------------------------------------------------
# compiler.c_cpp.flags  ->  CCFLAGS/CXXFLAGS/ASFLAGS
# ------------------------------------------------------------
common_ccflags = [
    "-mcmodel=medany",
    "-mabi=lp64f",
    "-march=rv64imafc",

    "-fno-common",
    "-ffunction-sections",
    "-fdata-sections",
    "-fstrict-volatile-bitfields",
    "-fno-zero-initialized-in-bss",
    "-ffast-math",
    "-fno-math-errno",
    "-fsingle-precision-constant",

    "-Os",
    "-ggdb",

    "-Wall",
    "-Werror=all",
    "-Wno-error=unused-function",
    "-Wno-error=unused-but-set-variable",
    "-Wno-error=unused-variable",
    "-Wno-error=deprecated-declarations",
    "-Wno-multichar",
    "-Wextra",
    "-Werror=frame-larger-than=32768",
    "-Wno-unused-parameter",
    "-Wno-sign-compare",
    "-Wno-error=missing-braces",
    "-Wno-error=return-type",
    "-Wno-error=pointer-sign",
    "-Wno-missing-braces",
    "-Wno-strict-aliasing",
    "-Wno-implicit-fallthrough",
    "-Wno-missing-field-initializers",
    "-Wno-int-to-pointer-cast",
    "-Wno-error=comment",
    "-Wno-error=logical-not-parentheses",
    "-Wno-error=duplicate-decl-specifier",
    "-Wno-error=parentheses",
]

env.Append(CCFLAGS=common_ccflags)
env.Append(CXXFLAGS=common_ccflags)
env.Append(ASFLAGS=common_ccflags + ["-x", "assembler-with-cpp"])


# ------------------------------------------------------------
# compiler.c.flags / compiler.cpp.flags  -> language standards + extra warnings
# ------------------------------------------------------------
env.Append(CFLAGS=[
    "-std=gnu11",
    "-Wno-pointer-to-int-cast",
    "-Wno-old-style-declaration",
])

env.Append(CXXFLAGS=[
    "-std=gnu++17",
])


# ------------------------------------------------------------
# compiler.ar.flags=cr  -> ARFLAGS
# ------------------------------------------------------------
env.Replace(ARFLAGS=["cr"])


# if not env.BoardConfig().get("build.ldscript", ""):
#     env.Replace(LDSCRIPT_PATH=join(SDK_DIR, "lds", "kendryte.ld"))

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