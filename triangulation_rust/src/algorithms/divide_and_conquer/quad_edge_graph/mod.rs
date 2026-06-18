mod quad_edge;
mod edge_entry;
mod edge_data;

use crate::geometry::functions::ccw_points;
use crate::geometry::{Point, Triangle};
pub(crate) use edge_data::EdgeData;
pub(crate) use edge_entry::EdgeEntry;
pub(crate) use quad_edge::QuadEdge;
use slotmap::{new_key_type, SlotMap};
use std::collections::BTreeSet;

new_key_type! {
    pub struct QEGraphKey;
}

pub(crate) struct QuadEdgeGraph {
    quad_edge_map: SlotMap<QEGraphKey, QuadEdge>,
}

impl QuadEdgeGraph {
    pub(crate) fn new() -> QuadEdgeGraph {
        QuadEdgeGraph {
            quad_edge_map: SlotMap::<QEGraphKey, QuadEdge>::with_key()
        }
    }

    fn get_edge_data(&self, entry: EdgeEntry) -> EdgeData {
        self.quad_edge_map[entry.quad_edge_key].edges[entry.edge_index as usize]
    }

    fn set_edge_data(&mut self, value: EdgeData, entry: EdgeEntry) {
        self.quad_edge_map[entry.quad_edge_key].edges[entry.edge_index as usize] = value;
    }

    fn get_next(&self, entry: EdgeEntry) -> EdgeEntry {
        self.quad_edge_map[entry.quad_edge_key].nexts[entry.edge_index as usize]
    }

    fn set_next(&mut self, value: EdgeEntry, entry: EdgeEntry) {
        self.quad_edge_map[entry.quad_edge_key].nexts[entry.edge_index as usize] = value;
    }

    pub(crate) fn splice(&mut self, a: EdgeEntry, b: EdgeEntry) {
        let alpha = a.onext(self).rot();
        let beta = b.onext(self).rot();

        let anext = self.get_next(a);
        self.set_next(self.get_next(b), a);
        self.set_next(anext, b);
        let alphanext = self.get_next(alpha);
        self.set_next(self.get_next(beta), alpha);
        self.set_next(alphanext, beta);
    }

    pub(crate) fn make_edge(&mut self, origin_data: EdgeData, dest_data: EdgeData) -> EdgeEntry {
        let key = self.quad_edge_map.insert_with_key(
            |key| QuadEdge::new(origin_data, dest_data, key)
        );
        EdgeEntry {
            edge_index: 0,
            quad_edge_key: key,
        }
    }

    pub(crate) fn make_edge_usize(&mut self, origin_data: usize, dest_data: usize) -> EdgeEntry {
        self.make_edge(EdgeData::Primary(origin_data), EdgeData::Primary(dest_data))
    }

    pub(crate) fn connect(&mut self, a: EdgeEntry, b: EdgeEntry) -> EdgeEntry {
        let edge = self.make_edge(a.dest(self), b.origin(self));
        self.splice(edge, a.lnext(self));
        self.splice(edge.sym(), b);
        edge
    }

    pub(crate) fn delete_edge(&mut self, edge: EdgeEntry) {
        self.splice(edge, edge.oprev(self));
        self.splice(edge.sym(), edge.sym().oprev(self));

        self.quad_edge_map.remove(edge.quad_edge_key);
    }


    fn get_valid_triangle(&self, e: EdgeEntry, points: &[Point]) -> Option<Triangle> {
        let lnext = e.lnext(self);

        if lnext.lnext(self).lnext(self) != e {
            return None;
        }

        if let (EdgeData::Primary(a), EdgeData::Primary(b), EdgeData::Primary(c)) =
            (e.origin(self), e.dest(self), lnext.dest(self))
        {
            let ccw = ccw_points(a, b, c, points);
            if ccw > 0f64 {
                return Some(Triangle { vertices: [a, b, c] });
            }
            if ccw < 0f64 {
                return Some(Triangle { vertices: [a, c, b] });
            }
            return Some(Triangle { vertices: [a, b, c] });
        }
        None
    }

    pub(crate) fn extract_all_triangles(
        &self,
        points: &[Point],
        sorted_to_original: &[usize],
    ) -> Vec<Triangle> {
        // Dedup key: sorted vertex tuple of the raw traversal (independent
        // of edge direction). Value: the CCW triple so the emitted
        // triangles all have consistent orientation.
        let mut triangles: std::collections::BTreeMap<[usize; 3], Triangle> =
            std::collections::BTreeMap::new();

        for (key, _) in self.quad_edge_map.iter() {
            for edge_index in [0, 2] {
                let e = EdgeEntry { quad_edge_key: key, edge_index };

                if let Some(triangle) = self.get_valid_triangle(e, points) {
                    let original = triangle.vertices.map(|v| sorted_to_original[v]);
                    let mut key = original;
                    key.sort_unstable();
                    triangles.entry(key).or_insert(Triangle { vertices: original });
                }
            }
        }

        triangles.into_values().collect()
    }
}