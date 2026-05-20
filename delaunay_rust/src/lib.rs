use pyo3::prelude::*;
use numpy::PyReadonlyArray2;

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

#[pyfunction]
fn triangulate_points<'py>(_py: Python<'py>, points_array: PyReadonlyArray2<'py, f64>) -> PyResult<Vec<[usize; 3]>> {
    let points_view = points_array.as_array();
    
    let mut points = Vec::with_capacity(points_view.shape()[0] + 3);
    for row in points_view.rows() {
        points.push(Point { x: row[0], y: row[1] });
    }

    println!("{}", points.len());
    
    Ok(vec![])
}

#[pymodule]
fn delaunay_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(triangulate_points, m)?)?;
    Ok(())
}