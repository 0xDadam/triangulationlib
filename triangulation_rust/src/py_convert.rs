use crate::geometry::{Point, Triangle};
use numpy::PyReadonlyArray2;

pub trait RustToPy<T> {
    fn to_py(self) -> T;
}

impl RustToPy<Vec<[usize; 3]>> for Vec<Triangle> {
    fn to_py(self) -> Vec<[usize; 3]> {
        self.into_iter().map(|t| t.vertices).collect()
    }
}

pub trait ToPointsVector {
    fn to_rust_point_vec(self) -> Vec<Point>;
}

impl<'py> ToPointsVector for PyReadonlyArray2<'py, f64> {
    fn to_rust_point_vec(self) -> Vec<Point> {
        self.as_array()
            .rows()
            .into_iter()
            .map(|row| Point::new(row[0], row[1]))
            .collect()
    }
}