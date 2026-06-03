#[derive(Clone, Copy, Debug, Ord, Eq, PartialEq, PartialOrd)]
pub struct Triangle {
    pub(crate) vertices: [usize; 3],
}