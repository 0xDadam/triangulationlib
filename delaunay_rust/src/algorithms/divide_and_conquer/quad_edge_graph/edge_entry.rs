use crate::algorithms::divide_and_conquer::quad_edge_graph::edge_data::EdgeData;
use crate::algorithms::divide_and_conquer::quad_edge_graph::{QEGraphKey, QuadEdgeGraph};
use crate::geometry::functions::ccw_points;
use crate::geometry::Point;

#[derive(Copy, Clone, PartialEq, Eq, Hash, Debug)]
pub(crate) struct EdgeEntry {
    pub(crate) edge_index: u8,
    pub(crate) quad_edge_key: QEGraphKey,
}

impl EdgeEntry {
    #[inline]
    pub(crate) fn rot(self) -> EdgeEntry {
        EdgeEntry {
            edge_index: (self.edge_index + 1) % 4,
            quad_edge_key: self.quad_edge_key,
        }
    }

    #[inline]
    pub(crate) fn sym(self) -> EdgeEntry {
        EdgeEntry {
            edge_index: (self.edge_index + 2) % 4,
            quad_edge_key: self.quad_edge_key,
        }
    }

    #[inline]
    pub(crate) fn rot_inv(self) -> EdgeEntry {
        EdgeEntry {
            edge_index: (self.edge_index + 3) % 4,
            quad_edge_key: self.quad_edge_key,
        }
    }

    #[inline]
    pub(crate) fn onext(self, graph: &QuadEdgeGraph) -> EdgeEntry {
        graph.get_next(self)
    }

    #[inline]
    pub(crate) fn oprev(self, graph: &QuadEdgeGraph) -> EdgeEntry {
        self.rot().onext(graph).rot()
    }

    #[inline]
    pub(crate) fn lnext(self, graph: &QuadEdgeGraph) -> EdgeEntry {
        self.rot_inv().onext(graph).rot()
    }

    #[inline]
    pub(crate) fn lprev(self, graph: &QuadEdgeGraph) -> EdgeEntry {
        self.onext(graph).sym()
    }

    #[inline]
    pub(crate) fn rnext(self, graph: &QuadEdgeGraph) -> EdgeEntry {
        self.rot().onext(graph).rot_inv()
    }

    #[inline]
    pub(crate) fn rprev(self, graph: &QuadEdgeGraph) -> EdgeEntry {
        self.sym().onext(graph)
    }

    #[inline]
    pub(crate) fn dnext(self, graph: &QuadEdgeGraph) -> EdgeEntry {
        self.sym().onext(graph).sym()
    }

    #[inline]
    pub(crate) fn dprev(self, graph: &QuadEdgeGraph) -> EdgeEntry {
        self.rot_inv().onext(graph).rot_inv()
    }

    #[inline]
    pub(crate) fn origin(self, graph: &QuadEdgeGraph) -> EdgeData {
        graph.get_edge_data(self)
    }

    #[inline]
    pub(crate) fn set_origin(self, value: EdgeData, graph: &mut QuadEdgeGraph) {
        graph.set_edge_data(value, self);
    }

    #[inline]
    pub(crate) fn dest(self, graph: &QuadEdgeGraph) -> EdgeData {
        graph.get_edge_data(self.sym())
    }

    #[inline]
    pub(crate) fn set_dest(self, value: EdgeData, graph: &mut QuadEdgeGraph) {
        graph.set_edge_data(value, self.sym());
    }

    pub(crate) fn to_left(self, a: EdgeData, points: &[Point], graph: &QuadEdgeGraph) -> bool {
        if let (EdgeData::Primary(a), EdgeData::Primary(b), EdgeData::Primary(c)) =
            (a, self.origin(graph), self.dest(graph))
        {
            return ccw_points(a, b, c, points) > 0f64;
        }
        panic!("Accessing Dual Graph edges")
    }

    pub(crate) fn to_right(self, a: EdgeData, points: &[Point], graph: &QuadEdgeGraph) -> bool {
        if let (EdgeData::Primary(a), EdgeData::Primary(b), EdgeData::Primary(c)) =
            (a, self.origin(graph), self.dest(graph))
        {
            return ccw_points(a, c, b, points) > 0f64;
        }
        panic!("Accessing Dual Graph edges")
    }
}