// NOT ORIGINAL SOURCE. Compile-only placeholder for the missing MarchingCubes.h.
//
// The recovered Mesh.h includes "MarchingCubes.h", which was intentionally
// not republished (its redistribution provenance is unestablished). Sculptor.h's
// carving path (Reset, SculpAccurate, SculpFast, isInMap, Project) never uses
// it. Only ToShape/PoligolizeCell/BuildCell use GRIDCELL and Polygonise, and
// those template members are never instantiated by the harness.
//
// Polygonise is therefore DECLARED BUT NOT DEFINED. Any harness code that tried
// to build a mesh would fail to link instead of silently using a substitute.
// The GRIDCELL layout below is inferred from BuildCell's use of cell->p[0..7]
// (Vector3DEx) and cell->val[0..7] (assigned 0.0f/1.0f). It is an assumption.
#pragma once
#include "Triangle.h"

typedef struct {
    Vector3DEx p[8];
    float val[8];
} GRIDCELL;

int Polygonise(GRIDCELL grid, double isolevel, Triangle **triangles);
