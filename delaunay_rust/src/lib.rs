pub mod geometry;
pub mod algorithms;
pub mod py_convert;

use numpy::PyReadonlyArray2;
use pyo3::prelude::*;

use crate::geometry::Point;
use crate::py_convert::TrianglesToPy;

#[pyfunction]
fn triangulate_points<'py>(_py: Python<'py>, points_array: PyReadonlyArray2<'py, f64>) -> PyResult<Vec<[usize; 3]>> {
    let points_view = points_array.as_array();
    
    let mut points = Vec::with_capacity(points_view.shape()[0] + 3);
    for row in points_view.rows() {
        points.push(Point::new(row[0], row[1]));
    }

    println!("{}", points.len());
    
    Ok(vec![])
}

#[pyfunction]
fn triangulate_points_dnc<'py>(_py: Python<'py>, points_array: PyReadonlyArray2<'py, f64>) -> PyResult<Vec<[usize; 3]>> {
    let points: Vec<Point> = points_array
        .as_array()
        .rows()
        .into_iter()
        .map(|row| Point::new(row[0], row[1] ))
        .collect();
    let triangles = algorithms::divide_and_conquer::triangulate(&points);
    Ok(triangles.to_py())
}

#[pymodule]
fn delaunay_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(triangulate_points, m)?)?;
    m.add_function(wrap_pyfunction!(triangulate_points_dnc, m)?)?;
    Ok(())
}