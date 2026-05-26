use slotmap::{new_key_type, SlotMap};

new_key_type! {
    struct QEGraphKey;
}

#[derive(Copy, Clone, Debug)]
enum EdgeData{
    Primary(usize),
    Dual
}

#[derive(Copy, Clone, Debug)]
struct QuadEdge {
    edges: [EdgeData; 4],
    nexts: [EdgeEntry; 4]
}

#[derive(Copy, Clone, PartialEq, Eq, Hash, Debug)]
pub struct EdgeEntry{
    edge_index: u8,
    quad_edge_key: QEGraphKey
}

impl EdgeEntry{
    #[inline]
    fn rot(self) -> EdgeEntry{
        EdgeEntry{
            edge_index: (self.edge_index + 1) % 4,
            quad_edge_key: self.quad_edge_key
        }
    }

    #[inline]
    fn sym(self) -> EdgeEntry{
        EdgeEntry{
            edge_index: (self.edge_index + 2) % 4,
            quad_edge_key: self.quad_edge_key
        }
    }

    #[inline]
    fn rot_inv(self) -> EdgeEntry{
        EdgeEntry{
            edge_index: (self.edge_index + 3) % 4,
            quad_edge_key: self.quad_edge_key
        }
    }

    #[inline]
    fn onext(self, graph: &QuadEdgeGraph) -> EdgeEntry{
        graph.get_next(self)
    }

    #[inline]
    fn oprev(self, graph: &QuadEdgeGraph) -> EdgeEntry{
        self.rot().onext(graph).rot()
    }

    #[inline]
    fn lnext(self, graph: &QuadEdgeGraph) -> EdgeEntry{
        self.rot_inv().onext(graph).rot()
    }

    #[inline]
    fn lprev(self, graph: &QuadEdgeGraph) -> EdgeEntry{
        self.onext(graph).sym()
    }

    #[inline]
    fn rnext(self, graph: &QuadEdgeGraph) -> EdgeEntry{
        self.rot().onext(graph).rot_inv()
    }

    #[inline]
    fn rprev(self, graph: &QuadEdgeGraph) -> EdgeEntry{
        self.sym().onext(graph)
    }

    #[inline]
    fn dnext(self, graph: &QuadEdgeGraph) -> EdgeEntry{
        self.sym().onext(graph).sym()
    }

    #[inline]
    fn dprev(self, graph: &QuadEdgeGraph) -> EdgeEntry{
        self.rot_inv().onext(graph).rot_inv()
    }

    fn origin(self, graph: &QuadEdgeGraph) -> EdgeData{
        graph.get_edge_data(self)
    }

    fn set_origin(self, value: EdgeData, graph: &mut QuadEdgeGraph){
        graph.set_edge_data(value, self);
    }

    fn dest(self, graph: &QuadEdgeGraph) -> EdgeData{
        graph.get_edge_data(self.sym())
    }

    fn set_dest(self, value: EdgeData, graph: &mut QuadEdgeGraph){
        graph.set_edge_data(value, self.sym());
    }
}

struct QuadEdgeGraph {
    quad_edge_map: SlotMap<QEGraphKey, QuadEdge>
}

impl QuadEdgeGraph{

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

    fn splice(&mut self, a: EdgeEntry, b: EdgeEntry){
        let alpha = a.onext(self).rot();
        let beta = b.onext(self).rot();

        let anext = self.get_next(a);
        self.set_next(self.get_next(b), a);
        self.set_next(anext, b);
        let alphanext = self.get_next(alpha);
        self.set_next(self.get_next(beta), alpha);
        self.set_next(alphanext, beta);
    }

    fn make_edge(origin_data: EdgeData, dest_data: EdgeData) -> EdgeEntry{

    }

}