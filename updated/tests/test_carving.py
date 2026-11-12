"""Synthetic geometric properties and comparisons to the actual original C++.

No historical camera captures, SDKs or research benchmark data are used.
"""
import math
import shutil
import sys
import unittest
from pathlib import Path

UPDATED = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UPDATED))
sys.path.insert(0,str(UPDATED/'harness'))
from demo import carve_demo, disk_views
from volume_carving_port import ACCURATE, FAST, SculptData, Sculptor, Vector3DEx


class GeometryTests(unittest.TestCase):
    def test_reset_and_bit_independence(self):
        s=Sculptor(16,16,(0,0,0))
        self.assertEqual(s.count_on(),4096)
        for v in ((0,0,0),(15,15,15),(2,3,7),(2,3,8)):
            s.turn_off(*v)
            self.assertFalse(s.is_on(*v))
        self.assertEqual(s.count_on(),4092)
        s.turn_on(2,3,8)
        self.assertEqual(s.count_on(),4093)
        s.reset()
        self.assertEqual(s.count_on(),4096)

    def test_project_hand_computed(self):
        p=[2,0,0,1, 0,3,0,-1, 0,0,1,1]
        self.assertEqual(Sculptor.project((1,2,3),p),(0.75,1.25))

    def test_zero_projection_denominator_is_outside(self):
        d=SculptData([0]*12,bytearray([255]),1,1)
        s=Sculptor(8,8,(0,0,0))
        s.sculp(d)
        self.assertEqual(s.count_on(),512)

    def test_foreground_and_background_extremes(self):
        for value,expected in ((0,0),(255,4096)):
            d=disk_views(16,5)[0]
            d.map[:]=bytes([value])*len(d.map)
            s=Sculptor(16,16,(0,0,0));s.sculp(d)
            self.assertEqual(s.count_on(),expected)

    def test_disk_intersection_matches_analytic_voxel_set(self):
        s,counts=carve_demo(16,5)
        c=7.5
        expected={(x,y,z) for x in range(16) for y in range(16) for z in range(16)
                  if (x-c)**2+(y-c)**2<=25 and (x-c)**2+(z-c)**2<=25 and (y-c)**2+(z-c)**2<=25}
        self.assertEqual(set(s.occupied()),expected)
        self.assertTrue(all(b<=a for a,b in zip(counts,counts[1:])))
        self.assertTrue(0<len(expected)<16**3)

    def test_view_order_invariance_of_accurate_carving(self):
        a,_=carve_demo(16,5)
        b=Sculptor(16,16,(0,0,0))
        for view in reversed(disk_views(16,5)):b.sculp(view)
        self.assertEqual(a.bits_hex(),b.bits_hex())

    def test_repeated_view_is_idempotent(self):
        s=Sculptor(16,16,(0,0,0));d=disk_views(16,5)[0]
        s.sculp(d);before=s.bits_hex();s.sculp(d)
        self.assertEqual(before,s.bits_hex())

    def test_fast_matches_accurate_on_convex_synthetic_views(self):
        a,_=carve_demo(16,5,ACCURATE);b,_=carve_demo(16,5,FAST)
        self.assertEqual(a.bits_hex(),b.bits_hex())

    def test_point_cloud_has_correct_header_and_rows(self):
        s,_=carve_demo(16,5)
        rows=s.to_ply().splitlines();idx=rows.index('end_header')
        self.assertIn(f'element vertex {s.count_on()}',rows)
        self.assertEqual(len(rows)-idx-1,s.count_on())
        self.assertTrue(all(len(r.split())==3 for r in rows[idx+1:]))

    def test_outline_has_twelve_edges(self):
        s=Sculptor(16,16,(0,0,0))
        self.assertEqual(len(s.create_outline()),12)
        self.assertEqual(len({p for edge in s.create_outline() for p in edge}),8)

    def test_size_limits_and_map_shape(self):
        for size in (0,7,9,136):
            with self.assertRaises(ValueError):Sculptor(size,1,(0,0,0))
        with self.assertRaises(ValueError):SculptData([0]*12,bytearray(2),2,2)


class OriginalVectorQuirks(unittest.TestCase):
    def test_stale_cached_length_regression(self):
        a,b=Vector3DEx(3,0,0),Vector3DEx(0,4,0)
        total=a+b;cross=a.cross(b)
        self.assertEqual((total.x,total.y,total.z),(3,4,0))
        self.assertEqual(total.length(),0)
        self.assertEqual(math.hypot(total.x,total.y,total.z),5)
        self.assertEqual((cross.x,cross.y,cross.z),(0,0,12))
        self.assertEqual(cross.length(),0)

    def test_normalize_preserves_original_receiver_mutation(self):
        v=Vector3DEx(3,4,0);n=v.normalize()
        self.assertAlmostEqual(n.length(),1,places=6)
        self.assertAlmostEqual(v.x,0.6,places=6)
        self.assertEqual(v.length(),5)  # cache deliberately remains stale


@unittest.skipUnless(shutil.which('clang++') or shutil.which('g++'),'needs C++ compiler')
class CompiledOriginalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from build_original import build
        cls.executables=build('strict')

    def test_original_accurate_bits_and_mutated_masks(self):
        from compare_with_original import compare
        result=compare(disk_views(16,5),mode=ACCURATE,exes=self.executables)
        self.assertTrue(result['exact'])

    def test_original_fast_bits_and_mutated_masks(self):
        from compare_with_original import compare
        result=compare(disk_views(16,5),mode=FAST,exes=self.executables)
        self.assertTrue(result['exact'])

    def test_original_extreme_silhouettes(self):
        from compare_with_original import compare
        for value in (0,255):
            for mode in (ACCURATE,FAST):
                d=disk_views(16,5)[0];d.map[:]=bytes([value])*len(d.map)
                self.assertTrue(compare([d],mode=mode,exes=self.executables)['exact'])


if __name__=='__main__':unittest.main()
