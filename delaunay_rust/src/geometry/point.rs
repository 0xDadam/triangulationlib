#[derive(Clone, Copy, Debug)]
pub struct Point {
    x: f64,
    y: f64,
}

impl Point {
    #[inline]
    pub fn x(&self) -> f64 {
        self.x
    }

    #[inline]
    pub fn y(&self) -> f64 {
        self.y
    }

    #[inline]
    pub fn new(x: f64, y: f64) -> Self {
        Self { x, y }
    }
}