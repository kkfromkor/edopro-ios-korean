#ifndef EDOPRO_IOS_LAYOUT_H
#define EDOPRO_IOS_LAYOUT_H

#include <cmath>

namespace porting {
namespace ios {

struct TouchPosition {
	int x;
	int y;
};

// Irrlicht's native iOS device emits UIKit points multiplied by UIScreen.scale,
// while its framebuffer uses nativeScale. Use the actual view/framebuffer sizes
// so Display Zoom and a resized landscape view also map to the rendered image.
inline TouchPosition framebufferTouch(TouchPosition input, double inputScale,
		double originX, double originY, double viewWidth, double viewHeight,
		unsigned framebufferWidth, unsigned framebufferHeight) {
	if(inputScale <= 0 || viewWidth <= 0 || viewHeight <= 0
			|| !framebufferWidth || !framebufferHeight)
		return input;
	return {
		static_cast<int>(std::lround((input.x / inputScale - originX) * framebufferWidth / viewWidth)),
		static_cast<int>(std::lround((input.y / inputScale - originY) * framebufferHeight / viewHeight))
	};
}

// Upgrade existing installs once; later changes in the in-game settings survive.
inline void migrateLayout(float& dpiScale, int& version) {
	if(version < 1) {
		dpiScale = 2.f;
		version = 1;
	}
}

}
}

#endif
