"""
OCCT build tasks using Invoke.

Usage:
    invoke build      # Configure and build OCCT
    invoke clean      # Clean build artifacts
    invoke rebuild    # Clean + build from scratch
    invoke install    # Install built OCCT
    invoke status     # Show build status
    invoke draw       # Launch DRAWEXE test environment
"""

import os
import sys
import multiprocessing
from invoke import task

# Configuration defaults
OCCT_ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(OCCT_ROOT, "build")
BUILD_TYPE = os.environ.get("OCCT_BUILD_TYPE", "Release")
JOBS = os.environ.get("OCCT_JOBS", str(multiprocessing.cpu_count()))

# OCCT Linux output layout: build/lin64/gcc/{bin,lib}
# Try to auto-detect the actual library/binary directories inside build

def _get_build_subdirs():
    """Auto-detect OCCT's build output subdirectories."""
    lib_dir = os.path.join(BUILD_DIR, "lib")
    bin_dir = os.path.join(BUILD_DIR, "bin")
    
    # On Linux, OCCT uses build/lin64/gcc/lib etc.
    if sys.platform.startswith("linux"):
        for candidate in ["lin64/gcc", "lin64/clang", "linux/gcc", "linux/clang"]:
            cand_lib = os.path.join(BUILD_DIR, candidate, "lib")
            cand_bin = os.path.join(BUILD_DIR, candidate, "bin")
            if os.path.isdir(cand_lib):
                lib_dir = cand_lib
                bin_dir = cand_bin
                break
    elif sys.platform == "darwin":
        for candidate in ["mac64/gcc", "mac64/clang", "osx/gcc", "osx/clang"]:
            cand_lib = os.path.join(BUILD_DIR, candidate, "lib")
            cand_bin = os.path.join(BUILD_DIR, candidate, "bin")
            if os.path.isdir(cand_lib):
                lib_dir = cand_lib
                bin_dir = cand_bin
                break
    elif sys.platform == "win32":
        for candidate in ["win64/vc", "win32/vc", "win64/gcc", "win32/gcc"]:
            cand_lib = os.path.join(BUILD_DIR, candidate, "lib")
            cand_bin = os.path.join(BUILD_DIR, candidate, "bin")
            if os.path.isdir(cand_lib):
                lib_dir = cand_lib
                bin_dir = cand_bin
                break
    
    return lib_dir, bin_dir


def run(c, cmd, **kwargs):
    """Run a shell command with error handling."""
    print(f"\n[RUN] {cmd}\n")
    result = c.run(cmd, pty=True, **kwargs)
    if result.exited != 0:
        raise RuntimeError(f"Command failed with exit code {result.exited}: {cmd}")
    return result


@task
def configure(c, build_type=None, install_prefix=None):
    """
    Configure OCCT with CMake.
    
    Options:
        --build-type: Release, Debug, RelWithDebInfo (default: Release)
        --install-prefix: Installation directory (default: /usr/local)
    """
    bt = build_type or BUILD_TYPE
    prefix = install_prefix or os.path.join(OCCT_ROOT, "install")

    os.makedirs(BUILD_DIR, exist_ok=True)

    cmd = (
        f"cmake -S {OCCT_ROOT} -B {BUILD_DIR} "
        f"-DCMAKE_BUILD_TYPE={bt} "
        f"-DCMAKE_INSTALL_PREFIX={prefix} "
        f"-DBUILD_LIBRARY_TYPE=Shared "
        f"-DBUILD_CPP_STANDARD=C++17"
    )

    run(c, cmd)
    print(f"\n[OK] Configuration complete. Build dir: {BUILD_DIR}")
    print(f"[OK] Install prefix: {prefix}")


@task
def build(c, build_type=None, jobs=None):
    """
    Build OCCT. Configures first if build directory doesn't exist.
    
    Options:
        --build-type: CMake build type override
        --jobs: Number of parallel build jobs (default: auto)
    """
    j = jobs or JOBS
    bt = build_type or BUILD_TYPE

    # Auto-configure if never configured
    if not os.path.exists(os.path.join(BUILD_DIR, "CMakeCache.txt")):
        print("[INFO] Build directory not configured yet. Running configure first...")
        configure(c, build_type=bt)

    # If build type explicitly changed, re-configure
    if build_type:
        configure(c, build_type=bt)

    cmd = f"cmake --build {BUILD_DIR} --config {bt} -j {j}"
    run(c, cmd)
    print(f"\n[OK] Build complete. Binaries in: {BUILD_DIR}")


@task
def clean(c):
    """
    Clean build artifacts. Removes the entire build directory.
    """
    if os.path.exists(BUILD_DIR):
        run(c, f"rm -rf {BUILD_DIR}")
        print(f"\n[OK] Cleaned build directory: {BUILD_DIR}")
    else:
        print(f"[INFO] Build directory does not exist: {BUILD_DIR}")


@task
def rebuild(c, build_type=None, jobs=None):
    """
    Clean and rebuild OCCT from scratch.
    
    Options:
        --build-type: CMake build type (default: Release)
        --jobs: Number of parallel build jobs
    """
    clean(c)
    build(c, build_type=build_type, jobs=jobs)


@task
def install(c, build_type=None, jobs=None):
    """
    Install OCCT to the configured prefix.
    Builds first if necessary.
    
    Options:
        --build-type: CMake build type
        --jobs: Number of parallel build jobs
    """
    j = jobs or JOBS
    bt = build_type or BUILD_TYPE

    if not os.path.exists(os.path.join(BUILD_DIR, "CMakeCache.txt")):
        print("[INFO] Not configured yet. Configuring and building first...")
        build(c, build_type=bt, jobs=j)

    cmd = f"cmake --build {BUILD_DIR} --config {bt} --target install -j {j}"
    run(c, cmd)
    
    # Read actual install prefix from CMake cache
    install_prefix = "/usr/local"
    cache_file = os.path.join(BUILD_DIR, "CMakeCache.txt")
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            for line in f:
                if line.startswith("CMAKE_INSTALL_PREFIX:"):
                    install_prefix = line.split("=")[-1].strip()
                    break
    
    print(f"\n[OK] Install complete. Installed to: {install_prefix}")


@task
def status(c):
    """
    Show current build status.
    """
    lib_dir, bin_dir = _get_build_subdirs()
    
    print(f"OCCT Root:        {OCCT_ROOT}")
    print(f"Build Directory:  {BUILD_DIR}")
    print(f"Build Type:       {BUILD_TYPE}")
    print(f"Parallel Jobs:    {JOBS}")
    print(f"Library Dir:      {lib_dir}")
    print(f"Binary Dir:       {bin_dir}")

    if os.path.exists(os.path.join(BUILD_DIR, "CMakeCache.txt")):
        print("Configure Status: CONFIGURED")
        so_files = []
        if os.path.exists(lib_dir):
            so_files = [f for f in os.listdir(lib_dir) if f.endswith(".so") or f.endswith(".dll") or f.endswith(".dylib")]
        print(f"Built Libraries:  {len(so_files)} files")
        
        drawexe = os.path.join(bin_dir, "DRAWEXE")
        if os.path.exists(drawexe):
            print(f"DRAWEXE:          FOUND ({drawexe})")
        else:
            print(f"DRAWEXE:          NOT FOUND")
    else:
        print("Configure Status: NOT CONFIGURED")
        print("Built Libraries:  0")


@task
def draw(c):
    """
    Launch OCCT DRAWEXE test environment.
    Sets up necessary environment variables automatically.
    """
    lib_dir, bin_dir = _get_build_subdirs()
    drawexe = os.path.join(bin_dir, "DRAWEXE")
    
    if not os.path.exists(drawexe):
        print(f"[ERROR] DRAWEXE not found at {drawexe}")
        print("[INFO] Run 'invoke build' first.")
        return
    
    # OCCT needs these env vars to run properly
    env_vars = [
        f"CASROOT={OCCT_ROOT}",
        f"CSF_OCCTResourcePath={OCCT_ROOT}/resources",
        f"CSF_DrawPluginDefaults={OCCT_ROOT}/resources/DrawResources",
        f"LD_LIBRARY_PATH={lib_dir}:$LD_LIBRARY_PATH",
    ]
    env_setup = "; ".join([f"export {v}" for v in env_vars])
    cmd = f"{env_setup}; {drawexe}"
    
    print(f"[INFO] Launching DRAWEXE...")
    for v in env_vars:
        print(f"[INFO] {v}")
    run(c, cmd)
