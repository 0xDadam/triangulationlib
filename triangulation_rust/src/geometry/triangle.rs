#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub struct Triangle {
    pub vertices: [usize; 3],
}

impl Triangle {
    #[inline]
    pub fn new(vertices: [usize; 3]) -> Self {
        Self { vertices }
    }

    #[inline]
    pub fn vertices(&self) -> [usize; 3] {
        self.vertices
    }
}