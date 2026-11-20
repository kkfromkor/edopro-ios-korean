#!/usr/bin/env bash
# Linux cross-build using the same cctools/vcpkg packages as upstream.
set -euo pipefail
cd "$(dirname "$0")/../.."

CCTOOLS_ROOT=${CCTOOLS_ROOT:-/opt/cctools}
VCPKG_ROOT=${VCPKG_ROOT:-./vcpkg2}
export PATH="$CCTOOLS_ROOT/clang/bin:$CCTOOLS_ROOT/bin:$PATH"
export CC="$CCTOOLS_ROOT/bin/arm64-iphoneos-clang"
export CXX="$CCTOOLS_ROOT/bin/arm64-iphoneos-clang++"
export AR="$CCTOOLS_ROOT/clang/bin/llvm-ar"
export RANLIB="$CCTOOLS_ROOT/bin/arm-apple-darwin11-ranlib"
export LDFLAGS="$CCTOOLS_ROOT/darwin/libclang_rt.ios.a -Wl,-dead_strip_dylibs"

for tool in "$CC" "$CXX" "$AR" ./premake5; do
    if [[ ! -x "$tool" ]]; then
        echo "Missing build tool: $tool. See porting/ios/README.md." >&2
        exit 1
    fi
done
if [[ ! -d "$VCPKG_ROOT/installed/arm64-ios" ]]; then
    echo "Missing arm64-ios dependencies in $VCPKG_ROOT/installed." >&2
    exit 1
fi

python3 porting/ios/prepare_resources.py
# The ygopro target links the checked-out core/Lua into the app itself.
# Do not add --no-core: that would remove this build target.
./premake5 gmake2 --architecture=arm64 --os=ios \
    --vcpkg-root="$VCPKG_ROOT" --sound=miniaudio --no-direct3d --no-joystick=true \
    --bundled-font=porting/ios/fonts/NotoSansCJKkr-Regular.otf
make -C build -j"${BUILD_JOBS:-$(nproc)}" config=release_arm64 ygopro
python3 porting/ios/package_app.py bin/arm64/release/ygopro.app
