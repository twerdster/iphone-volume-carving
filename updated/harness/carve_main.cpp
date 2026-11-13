// Reference driver for the ORIGINAL Sculptor<Size> carving code (new harness
// code, 2026). Sculptor.h and its dependencies are compiled unmodified from
// ../../source/Sculptor. Only MarchingCubes.h comes from ./compat (see there).
//
// Input (text):
//   Size scaleRate tx ty tz nViews
//   then per view:  mode(0=ACCURATE,1=FAST) sizeX sizeY
//                   p0 ... p11              (row-major 3x4, decimal floats)
//                   <hex string of sizeX*sizeY map bytes>
// Output (text), per view:  "view i on=<count>" + mutated map hex
//   final: bits hex, then margins.
#include "Sculptor.h"
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <cctype>

// Optional third argument: an existing directory for exact per-view occupancy
// snapshots. This affects harness output only, never the recovered algorithm.
static std::string snapshotDirectory;

template <int Size>
struct Probe : public Sculptor<Size> {
    Probe(float s, const Vector3D &t) : Sculptor<Size>(s, t) {}
    int countOn() {
        int n = 0;
        for (int x = 0; x < Size; x++)
            for (int y = 0; y < Size; y++)
                for (int z = 0; z < Size; z++)
                    n += this->IsOn(x, y, z) ? 1 : 0;
        return n;
    }
    void dumpBits(FILE *out) {
        for (int x = 0; x < Size; x++)
            for (int y = 0; y < Size; y++)
                for (int z = 0; z < (Size >> 3); z++)
                    fprintf(out, "%02x", this->sculpture[x][y][z]);
        fprintf(out, "\n");
    }
    void dumpMargins(FILE *out) {
        MeshMargins<Size> &m = this->meshMargins;
        fprintf(out, "minX %d maxX %d\n", m.GetMinX(), m.GetMaxX());
        // raw arrays are private; read them through the clamping getters at
        // in-bounds coordinates only, which return the stored values unchanged
        fprintf(out, "Y");
        for (int x = m.GetMinX(); x <= m.GetMaxX(); x++)
            fprintf(out, " %d:%d-%d", x, m.GetMinYPerX(x), m.GetMaxYPerX(x));
        fprintf(out, "\nZ");
        for (int x = m.GetMinX(); x <= m.GetMaxX(); x++)
            for (int y = m.GetMinYPerX(x); y <= m.GetMaxYPerX(x); y++)
                fprintf(out, " %d,%d:%d-%d", x, y, m.GetMinZPerXY(x, y), m.GetMaxZPerXY(x, y));
        fprintf(out, "\n");
    }
};

static std::vector<unsigned char> fromHex(const std::string &h) {
    std::vector<unsigned char> v(h.size() / 2);
    for (size_t i = 0; i < v.size(); i++) v[i] = (unsigned char)strtol(h.substr(2 * i, 2).c_str(), nullptr, 16);
    return v;
}

template <int Size>
static int run(std::istream &in, FILE *out, float scale, float tx, float ty, float tz, int nViews) {
    Probe<Size> *s = new Probe<Size>(scale, Vector3D(tx, ty, tz));
    for (int v = 0; v < nViews; v++) {
        int mode, sx, sy;
        if (!(in >> mode >> sx >> sy) || sx < 1 || sy < 1 || sx > 4096 || sy > 4096 || mode < 0 || mode > 1) return 3;
        SculptData d;
        for (int k = 0; k < 12; k++) {
            if (!(in >> d.projection[k])) return 3;
        }
        std::string hex;
        const size_t expected = (size_t)sx * sy * 2;
        if (!(in >> std::setw(expected + 1) >> hex) || hex.size() != expected) return 3;
        for (unsigned char c : hex) if (!std::isxdigit(c)) return 3;
        std::vector<unsigned char> bytes = fromHex(hex);
        d.sizeXmap = sx;
        d.sizeYmap = sy;
        d.map = new unsigned char[(size_t)sx * sy];
        for (size_t i = 0; i < bytes.size(); i++) d.map[i] = bytes[i];
        s->Sculp(&d, mode == 1 ? FAST : ACCURATE);
        fprintf(out, "view %d on=%d\n", v, s->countOn());
        if (!snapshotDirectory.empty()) {
            char name[32];
            snprintf(name, sizeof name, "/view-%02d.hex", v+1);
            FILE *snapshot = fopen((snapshotDirectory + name).c_str(), "w");
            if (!snapshot) return 5;
            s->dumpBits(snapshot);
            fclose(snapshot);
        }
        for (int i = 0; i < sx * sy; i++) fprintf(out, "%02x", d.map[i]);
        fprintf(out, "\n");
        d.Clear();
    }
    s->dumpBits(out);
    s->dumpMargins(out);
    delete s;
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s IN OUT\n", argv[0]); return 1; }
    if (argc >= 4) snapshotDirectory = argv[3];
    std::ifstream in(argv[1]);
    FILE *out = fopen(argv[2], "w");
    if (!in || !out) return 2;
    int size, nViews;
    char a[64], b[64], c[64], d[64];
    if (!(in >> size >> std::setw(64) >> a >> std::setw(64) >> b >> std::setw(64) >> c >> std::setw(64) >> d >> nViews) || nViews < 0 || nViews > 1000) return 3;
    float scale = strtof(a, nullptr), tx = strtof(b, nullptr), ty = strtof(c, nullptr), tz = strtof(d, nullptr);
    int rc;
    switch (size) {
        case 16: rc = run<16>(in, out, scale, tx, ty, tz, nViews); break;
        case 24: rc = run<24>(in, out, scale, tx, ty, tz, nViews); break;
        case 32: rc = run<32>(in, out, scale, tx, ty, tz, nViews); break;
        case 64: rc = run<64>(in, out, scale, tx, ty, tz, nViews); break;
        case 128: rc = run<128>(in, out, scale, tx, ty, tz, nViews); break;
        default: fprintf(stderr, "unsupported size %d\n", size); rc = 4;
    }
    fclose(out);
    return rc;
}
