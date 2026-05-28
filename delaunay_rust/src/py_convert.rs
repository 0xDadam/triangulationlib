use crate::geometry::Triangle;

pub trait TrianglesToPy {
    fn to_py(self) -> Vec<[usize; 3]>;
}

impl TrianglesToPy for Vec<Triangle> {
    fn to_py(self) -> Vec<[usize; 3]> {
        self.into_iter().map(|t| t.vertices()).collect()
    }
}
