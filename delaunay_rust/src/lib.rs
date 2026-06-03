pub mod geometry;
pub mod algorithms;
pub mod py_convert;

use crate::geometry::Point;
use crate::py_convert::{RustToPy, ToPointsVector};
use numpy::PyReadonlyArray2;
use pyo3::prelude::*;

#[pyfunction]
#[pyo3(signature = (points_array, use_triangle_walk=true))]
fn triangulate_points<'py>(
    _py: Python<'py>,
    points_array: PyReadonlyArray2<'py, f64>,
    use_triangle_walk: bool,
) -> PyResult<Vec<[usize; 3]>> {
    let points: Vec<Point> = points_array.to_rust_point_vec();
    let triangles = algorithms::incremental::triangulate(&points, use_triangle_walk);
    Ok(triangles.to_py())
}


#[pyfunction]
#[pyo3(signature = (points_array))]
fn triangulate_points_dnc<'py>(_py: Python<'py>, points_array: PyReadonlyArray2<'py, f64>) -> PyResult<Vec<[usize; 3]>> {
    let points: Vec<Point> = points_array.to_rust_point_vec();
    let triangles = algorithms::divide_and_conquer::triangulate(&points);
    Ok(triangles.to_py())
}

#[pymodule]
fn delaunay_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(triangulate_points, m)?)?;
    m.add_function(wrap_pyfunction!(triangulate_points_dnc, m)?)?;
    Ok(())
}