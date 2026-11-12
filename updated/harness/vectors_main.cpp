// Probe of ORIGINAL Vector3DEx/Triangle semantics (new harness code, 2026).
// Vector3D.cpp, Vector3DEx.cpp and Triangle.cpp are compiled unmodified.
// Input: lines "ax ay az bx by bz cx cy cz". Output: one CSV row per line.
#include "Vector3DEx.h"
#include "Triangle.h"
#include <cstdio>
#include <cstdlib>

static void pv(FILE *o, Vector3DEx v) { fprintf(o, ",%.9g,%.9g,%.9g,%.9g", v.getX(), v.getY(), v.getZ(), v.length()); }

int main(int argc, char **argv) {
    if (argc < 3) return 1;
    FILE *in = fopen(argv[1], "r");
    FILE *o = fopen(argv[2], "w");
    if (!in || !o) return 2;
    char s[9][64];
    fprintf(o, "dot,angle,cmp_lt,cmp_gt,eq");
    const char *names[] = {"a", "diff", "sum", "cross", "scaled", "normalized", "a_after_normalize", "normal"};
    for (const char *n : names) fprintf(o, ",%s_x,%s_y,%s_z,%s_len", n, n, n, n);
    fprintf(o, "\n");
    while (fscanf(in, "%63s %63s %63s %63s %63s %63s %63s %63s %63s", s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8]) == 9) {
        float f[9];
        for (int i = 0; i < 9; i++) f[i] = strtof(s[i], nullptr);
        Vector3DEx a(f[0], f[1], f[2]), b(f[3], f[4], f[5]), c(f[6], f[7], f[8]);
        Vector3DEx a0 = a;
        fprintf(o, "%.9g,%.9g,%d,%d,%d", a * b, a.angle(b), (int)(a < b), (int)(a > b), (int)(a == b));
        pv(o, a0);
        pv(o, a - b);
        pv(o, a + b);
        pv(o, a.crossProduct(b));
        pv(o, a * 0.5f);
        Vector3DEx n = a.normalize();
        pv(o, n);
        pv(o, a);
        Triangle t(a0, b, c);
        pv(o, t.normal);
        fprintf(o, "\n");
    }
    fclose(in);
    fclose(o);
    return 0;
}
