#[derive(Clone, Copy, Debug)]
pub struct Triangle {
    vertices: [usize; 3],
}

impl Triangle {
    #[inline]
    pub fn vertices(&self) -> [usize; 3] {
        self.vertices
    }
}