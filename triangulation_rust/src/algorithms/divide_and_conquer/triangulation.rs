use super::quad_edge_graph::{EdgeData, EdgeEntry, QuadEdgeGraph};
use crate::geometry::functions::{ccw_points, in_circle_points};
use crate::geometry::{Point, Triangle};

pub fn triangulate(points: &[Point]) -> Vec<Triangle> {
    let mut sorted_to_original: Vec<usize> = (0..points.len()).collect();
    sorted_to_original.sort_unstable_by(|&a, &b| points[a].cmp(&points[b]));

    let sorted_points: Vec<Point> = sorted_to_original.iter().map(|&i| points[i]).collect();

    let mut qe_graph = QuadEdgeGraph::new();
    build_triangulation(0, sorted_points.len(), &sorted_points, &mut qe_graph);

    qe_graph.extract_all_triangles(&sorted_points, &sorted_to_original)
}

fn build_triangulation(
    start: usize,
    end: usize,
    points: &[Point],
    graph: &mut QuadEdgeGraph,
) -> (EdgeEntry, EdgeEntry) {
    let n = end - start;

    if n == 2 {
        let a = graph.make_edge_usize(start, start + 1);
        return (a, a.sym());
    }
    if n == 3 {
        let a = graph.make_edge_usize(start, start + 1);
        let b = graph.make_edge_usize(start + 1, start + 2);
        graph.splice(a.sym(), b);

        let c_val = ccw_points(start, start + 1, start + 2, points);
        return if c_val > 0f64 {
            graph.connect(b, a);
            (a, b.sym())
        } else if c_val < 0f64 {
            let c = graph.connect(b, a);
            (c.sym(), c)
        } else {
            (a, b.sym())
        };
    }

    let mid = (start + end) / 2;
    let (ldo_left, rdo_left) = build_triangulation(start, mid, points, graph);
    let (ldo_right, rdo_right) = build_triangulation(mid, end, points, graph);

    merge_triangulations(ldo_left, rdo_left, ldo_right, rdo_right, points, graph)
}


fn merge_triangulations(
    mut ldo_left: EdgeEntry,
    rdo_left: EdgeEntry,
    ldo_right: EdgeEntry,
    mut rdo_right: EdgeEntry,
    points: &[Point],
    graph: &mut QuadEdgeGraph,
) -> (EdgeEntry, EdgeEntry) {

    //lower tangent
    let mut ldo_inner = rdo_left;
    let mut rdo_inner = ldo_right;

    loop {
        if ldo_inner.to_left(rdo_inner.origin(graph), points, graph) {
            ldo_inner = ldo_inner.lnext(graph);
        } else if rdo_inner.to_right(ldo_inner.origin(graph), points, graph) {
            rdo_inner = rdo_inner.rprev(graph);
        } else {
            break
        }
    }
    let mut base_lre = graph.connect(rdo_inner.sym(), ldo_inner);

    if ldo_left.origin(graph) == ldo_inner.origin(graph) {
        ldo_left = base_lre.sym();
    }
    if rdo_right.origin(graph) == rdo_inner.origin(graph) {
        rdo_right = base_lre;
    }

    //the zipper
    loop {
        let mut lcand = base_lre.sym().onext(graph);
        if base_lre.to_right(lcand.dest(graph), points, graph) {
            while in_circle_points_unbox(
                base_lre.dest(graph),
                base_lre.origin(graph),
                lcand.dest(graph),
                lcand.onext(graph).dest(graph),
                points,
            ) {
                let t = lcand.onext(graph);
                graph.delete_edge(lcand);
                lcand = t;
            }
        }

        let mut rcand = base_lre.oprev(graph);
        if base_lre.to_right(rcand.dest(graph), points, graph) {
            while in_circle_points_unbox(
                base_lre.dest(graph),
                base_lre.origin(graph),
                rcand.dest(graph),
                rcand.oprev(graph).dest(graph),
                points,
            ) {
                let t = rcand.oprev(graph);
                graph.delete_edge(rcand);
                rcand = t;
            }
        }

        let l_valid = base_lre.to_right(lcand.dest(graph), points, graph);
        let r_valid = base_lre.to_right(rcand.dest(graph), points, graph);

        // Jeśli po obu stronach nie ma już kandydatów, kończymy zszywanie
        if !l_valid && !r_valid {
            break;
        }

        // Wybór kandydata do podłączenia nowej krawędzi LR
        if !l_valid || (r_valid && in_circle_points_unbox(
            lcand.dest(graph),
            lcand.origin(graph),
            rcand.origin(graph),
            rcand.dest(graph),
            points,
        )) {
            base_lre = graph.connect(rcand, base_lre.sym());
        } else {
            base_lre = graph.connect(base_lre.sym(), lcand.sym());
        }
    }

    // Zwrócenie krawędzi otoczki wypukłej połączonej triangulacji
    (ldo_left, rdo_right)
}


pub(crate) fn in_circle_points_unbox(a: EdgeData, b: EdgeData, c: EdgeData, d: EdgeData, points: &[Point]) -> bool {
    if let (EdgeData::Primary(a), EdgeData::Primary(b), EdgeData::Primary(c), EdgeData::Primary(d)) =
        (a, b, c, d) {
        return in_circle_points(a, b, c, d, points);
    }
    panic!()
}
