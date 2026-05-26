use crate::algorithms::divide_and_conquer::quad_edge_graph::edge_data::EdgeData;
use crate::algorithms::divide_and_conquer::quad_edge_graph::edge_entry::EdgeEntry;
use crate::algorithms::divide_and_conquer::quad_edge_graph::{QEGraphKey, QuadEdgeGraph};

#[derive(Copy, Clone, Debug)]
pub(crate) struct QuadEdge {
    pub(crate) edges: [EdgeData; 4],
    pub(crate) nexts: [EdgeEntry; 4]
}

impl QuadEdge{
    pub(crate) fn new(origin: EdgeData, dest: EdgeData, quad_edge_key: QEGraphKey) -> QuadEdge{
        let nexts = [0, 3, 2, 1]
            .map(| i  | EdgeEntry{edge_index: i as u8, quad_edge_key});
        QuadEdge{
            edges: [origin, EdgeData::Dual, dest, EdgeData::Dual],
            nexts
        }
    }
}