"""Generate PNG icons for the Solar Forecast PWA."""
import struct
import zlib
import math
import os


def make_icon_png(size):
    """
    Generate a sun icon PNG: amber gradient rounded-square background
    with a white sun (core + 8 rays) inside — matches the app header icon.
    """
    cx = cy = (size - 1) / 2.0
    corner_r = size * 0.22  # proportional corner radius

    core_r = size * 0.225
    outer_r = size * 0.42
    n_rays = 8

    rows = []
    for y in range(size):
        row = []
        for x in range(size):
            dx = x - cx
            dy = y - cy

            # Rounded-square check
            rx = max(0.0, abs(dx) - (size / 2 - corner_r - 0.5))
            ry = max(0.0, abs(dy) - (size / 2 - corner_r - 0.5))
            cdist = math.sqrt(rx * rx + ry * ry)

            if abs(dx) > size / 2 - 0.5 or abs(dy) > size / 2 - 0.5 or cdist > corner_r:
                row += [0, 0, 0, 0]  # transparent outside rounded rect
                continue

            # Amber → yellow gradient at 135°: #F5A623 → #F7C948
            t = max(0.0, min(1.0, (dx + dy) / (size * 0.7) + 0.5))
            bg_r = int(245 + (247 - 245) * t)
            bg_g = int(166 + (201 - 166) * t)
            bg_b = int(35 + (72 - 35) * t)

            # Sun shape
            sdist = math.sqrt(dx * dx + dy * dy) if (dx or dy) else 0.0

            is_sun = False
            if sdist <= core_r:
                is_sun = True
            elif sdist <= outer_r:
                angle = math.atan2(dy, dx)
                seg = (2 * math.pi) / n_rays
                norm = angle % seg
                dist_from_center = abs(norm - seg / 2) / (seg / 2)  # 0=ray center, 1=gap
                ray_frac = (sdist - core_r) / (outer_r - core_r)
                ray_half_width = 0.38 * (1 - ray_frac * 0.45)
                if dist_from_center < ray_half_width:
                    is_sun = True

            if is_sun:
                row += [255, 255, 255, 230]
            else:
                row += [bg_r, bg_g, bg_b, 255]

        rows.append(bytes(row))

    # Encode as RGBA PNG
    raw = b''.join(b'\x00' + r for r in rows)
    compressed = zlib.compress(raw, 9)

    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack('>II', size, size) + bytes([8, 6, 0, 0, 0])

    return (
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', ihdr)
        + chunk(b'IDAT', compressed)
        + chunk(b'IEND', b'')
    )


if __name__ == '__main__':
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'icons')
    os.makedirs(out_dir, exist_ok=True)
    for size in [48, 72, 96, 144, 192, 512]:
        data = make_icon_png(size)
        path = os.path.join(out_dir, f'icon-{size}.png')
        with open(path, 'wb') as f:
            f.write(data)
        print(f'  Generated {path}  ({len(data):,} bytes)')
    print('Done.')
