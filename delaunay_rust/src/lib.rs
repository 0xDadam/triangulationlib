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

    pub fn add_point(&mut self, point_idx: usize) {
        let p = &self.points[point_idx];
        let mut bad_triangles = Vec::new();

        for (i, tri) in self.triangles.iter().enumerate() {
            if tri.active {
                let a = &self.points[tri.vertices[0]];
                let b = &self.points[tri.vertices[1]];
                let c = &self.points[tri.vertices[2]];
                
                if in_circle(a, b, c, p) {
                    bad_triangles.push(i);
                }
            }
        }

        if bad_triangles.is_empty() { return; }

        let mut boundary: Vec<(usize, usize, Option<usize>)> = Vec::new();
        
        for &bad_idx in &bad_triangles {
            let tri = self.triangles[bad_idx];
            
            for i in 0..3 {
                let neighbor_idx = tri.neighbors[i];
                
                let is_boundary = match neighbor_idx {
                    Some(idx) => !bad_triangles.contains(&idx),
                    None => true,
                };

                if is_boundary {
                    boundary.push((tri.vertices[i], tri.vertices[(i + 1) % 3], neighbor_idx));
                }
            }
            
            self.triangles[bad_idx].active = false;
        }

        let mut new_triangles_indices = Vec::new();
        let base_idx = self.triangles.len();

        for (j, &(p1, p2, outer_neighbor)) in boundary.iter().enumerate() {
            let new_tri_idx = base_idx + j;
            
            let new_tri = Triangle {
                vertices: [p1, p2, point_idx],
                neighbors: [outer_neighbor, None, None], // zewnetrzny, nastepny, poprzedni
                active: true,
            };
            
            self.triangles.push(new_tri);
            new_triangles_indices.push(new_tri_idx);
        }

        // aktualizacja sasiadow poaza dziura
        for (j, &(_, p2, outer_neighbor)) in boundary.iter().enumerate() {
            let p1 = boundary[j].0;
            let new_tri_idx = base_idx + j;
            
            if let Some(n_idx) = outer_neighbor {
                let n_tri = &mut self.triangles[n_idx];
                for k in 0..3 {
                    //CCW
                    if n_tri.vertices[k] == p2 && n_tri.vertices[(k + 1) % 3] == p1 {
                        n_tri.neighbors[k] = Some(new_tri_idx);
                        break;
                    }
                }
            }
        }

        // _link_new_triangles
        for &t1_idx in &new_triangles_indices {
            for &t2_idx in &new_triangles_indices {
                if t1_idx == t2_idx { continue; }
                
                let v1_1 = self.triangles[t1_idx].vertices[1];
                let v1_0 = self.triangles[t1_idx].vertices[0];
                let v2_0 = self.triangles[t2_idx].vertices[0];
                let v2_1 = self.triangles[t2_idx].vertices[1];

                if v1_1 == v2_0 {
                    self.triangles[t1_idx].neighbors[1] = Some(t2_idx);
                }
                if v1_0 == v2_1 {
                    self.triangles[t1_idx].neighbors[2] = Some(t2_idx);
                }
            }
        }
    }
}

#[pyfunction]
fn triangulate_points<'py>(_py: Python<'py>, points_array: PyReadonlyArray2<'py, f64>) -> PyResult<Vec<[usize; 3]>> {
    let points_view = points_array.as_array();
    
    let num_input_points = points_view.shape()[0];
    let mut points = Vec::with_capacity(num_input_points + 3);
    
    for row in points_view.rows() {
        points.push(Point { x: row[0], y: row[1] });
    }

    let mut delaunay = DelaunayTriangulation::new(points);

    for i in 0..num_input_points {
        delaunay.add_point(i);
    }

    //usuwanie smieci
    let mut result = Vec::new();
    let super_p1 = num_input_points;
    let super_p2 = num_input_points + 1;
    let super_p3 = num_input_points + 2;

    for tri in delaunay.triangles {
        if tri.active {
            let is_super = tri.vertices.iter().any(|&v| v == super_p1 || v == super_p2 || v == super_p3);
            
            if !is_super {
                result.push(tri.vertices);
            }
        }
    }

    Ok(result)
}

#[pymodule]
fn delaunay_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(triangulate_points, m)?)?;
    Ok(())
}