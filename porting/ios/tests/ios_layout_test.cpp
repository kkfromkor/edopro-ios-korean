#include "../../../gframe/iOS/ios_layout.h"
#include <cassert>
#include <initializer_list>

int main() {
	using porting::ios::framebufferTouch;
	using porting::ios::TouchPosition;
	// Center, corners and an arbitrary card position on ordinary Retina screens,
	// downsampled Plus screens and Display Zoom. The old code fails the latter.
	struct Screen { double width, height, scale; unsigned pixelsX, pixelsY; };
	for(const auto screen : {
			Screen{844, 390, 3, 2532, 1170},
			Screen{736, 414, 3, 1920, 1080},
			Screen{667, 375, 3, 1920, 1080},
			Screen{1024, 768, 2, 2048, 1536},
			Screen{852, 393, 3, 1179, 2556}}) {
		for(const double x : {0., .25, .5, .9, 1.}) {
			for(const double y : {0., .25, .5, .9, 1.}) {
				const TouchPosition raw{int(x * screen.width * screen.scale), int(y * screen.height * screen.scale)};
				const auto mapped = framebufferTouch(raw, screen.scale, 0, 0,
					screen.width, screen.height, screen.pixelsX, screen.pixelsY);
				assert(std::abs(mapped.x - x * screen.pixelsX) <= 3);
				assert(std::abs(mapped.y - y * screen.pixelsY) <= 3);
			}
		}
	}
	// View-local origin, zero-sized layout during rotation, and drag outside view.
	auto point = framebufferTouch({60, 120}, 3, 10, 20, 100, 200, 200, 400);
	assert(point.x == 20 && point.y == 40);
	point = framebufferTouch({60, 120}, 3, 0, 0, 0, 200, 200, 400);
	assert(point.x == 60 && point.y == 120);
	point = framebufferTouch({-30, 660}, 3, 0, 0, 100, 200, 200, 400);
	assert(point.x == -20 && point.y == 440);
	// Existing 100% configuration upgrades to 200%; user's later 175% survives.
	float scale = 1.f;
	int version = 0;
	porting::ios::migrateLayout(scale, version);
	assert(scale == 2.f && version == 1);
	scale = 1.75f;
	porting::ios::migrateLayout(scale, version);
	assert(scale == 1.75f && version == 1);
}
