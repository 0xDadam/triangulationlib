use crate::geometry::Point;

pub fn ccw(pa: Point, pb: Point, pc: Point) -> f64 {
    ((pb.x() - pa.x()) * (pc.y() - pa.y())) - ((pb.y() - pa.y()) * (pc.x() - pa.x()))
}

pub fn ccw_points(a: usize, b: usize, c: usize, points: &[Point]) -> f64 {
    ccw(points[a], points[b], points[c])
}

pub fn in_circle(a: Point, b: Point, c: Point, d: Point) -> bool {
    let adx = a.x() - d.x();
    let ady = a.y() - d.y();

    let bdx = b.x() - d.x();
    let bdy = b.y() - d.y();

    let cdx = c.x() - d.x();
    let cdy = c.y() - d.y();

    let alift = adx * adx + ady * ady;
    let blift = bdx * bdx + bdy * bdy;
    let clift = cdx * cdx + cdy * cdy;

    let det = alift * (bdx * cdy - cdx * bdy)
        + blift * (cdx * ady - adx * cdy)
        + clift * (adx * bdy - bdx * ady);

    det > 0.0
}

pub fn in_circle_points(a: usize, b: usize, c: usize, d: usize, points: &[Point]) -> bool {
    in_circle(points[a], points[b], points[c], points[d])
}