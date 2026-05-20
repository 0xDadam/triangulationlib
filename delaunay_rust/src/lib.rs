use pyo3::prelude::*;
use numpy::PyReadonlyArray2;

const EPS: f64 = 1e-12;

#[derive(Clone, Copy, Debug)]
struct Point {
    x: f64,
    y: f64,
}

#[derive(Clone, Copy, Debug)]
struct Triangle {
    vertices: [usize; 3],
    neighbors: [Option<usize>; 3],
    active: bool,
}

fn det_orient(a: &Point, b: &Point, c: &Point) -> f64 {
    (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
}

fn in_circle(a: &Point, b: &Point, c: &Point, d: &Point) -> bool {
    let ax = a.x - d.x; let ay = a.y - d.y;
    let bx = b.x - d.x; let by = b.y - d.y;
    let cx = c.x - d.x; let cy = c.y - d.y;

    let det = (ax * ax + ay * ay) * (bx * cy - cx * by) -
              (bx * bx + by * by) * (ax * cy - cx * ay) +
              (cx * cx + cy * cy) * (ax * by - bx * ay);

    det > EPS
}

struct DelaunayTriangulation {
    points: Vec<Point>,
    triangles: Vec<Triangle>,
}

impl DelaunayTriangulation {
    fn new(mut points: Vec<Point>) -> Self {
        let mut min_x = f64::MAX; let mut min_y = f64::MAX;
        let mut max_x = f64::MIN; let mut max_y = f64::MIN;

        for p in &points {
            if p.x < min_x { min_x = p.x; }
            if p.y < min_y { min_y = p.y; }
            if p.x > max_x { max_x = p.x; }
            if p.y > max_y { max_y = p.y; }
        }

        let dx = max_x - min_x;
        let dy = max_y - min_y;
        let delta_max = if dx > dy { dx } else { dy };
        let mid_x = (min_x + max_x) / 2.0;
        let mid_y = (min_y + max_y) / 2.0;

        let p1 = Point { x: mid_x - 20.0 * delta_max, y: mid_y - delta_max };
        let p2 = Point { x: mid_x, y: mid_y + 20.0 * delta_max };
        let p3 = Point { x: mid_x + 20.0 * delta_max, y: mid_y - delta_max };

        let p1_idx = points.len();
        let p2_idx = points.len() + 1;
        let p3_idx = points.len() + 2;

        points.push(p1);
        points.push(p2);
        points.push(p3);

        let super_triangle = Triangle {
            vertices: [p1_idx, p2_idx, p3_idx],
            neighbors: [None, None, None],
            active: true,
        };

        let mut triangles = Vec::with_capacity(points.len() * 2);
        triangles.push(super_triangle);

        Self { points, triangles }
    }
}

#[pyfunction]
fn triangulate_points<'py>(_py: Python<'py>, points_array: PyReadonlyArray2<'py, f64>) -> PyResult<Vec<[usize; 3]>> {
    let points_view: numpy::ndarray::prelude::ArrayBase<numpy::ndarray::ViewRepr<&f64>, numpy::ndarray::prelude::Dim<[usize; 2]>> = points_array.as_array();

    let mut points = Vec::with_capacity(points_view.shape()[0] + 3);
    for row in points_view.rows() {
        points.push(Point { x: row[0], y: row[1] });
    }

    let delaunay = DelaunayTriangulation::new(points);
    println!("{} punktow, {} trojkatow.", delaunay.points.len(), delaunay.triangles.len());

    Ok(vec![])
}

#[pymodule]
fn delaunay_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(triangulate_points, m)?)?;
    Ok(())
}