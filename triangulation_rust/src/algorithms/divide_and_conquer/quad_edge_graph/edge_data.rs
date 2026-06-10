#[derive(Copy, Clone, Debug, PartialEq)]
pub(crate) enum EdgeData {
    Primary(usize),
    Dual,
}

