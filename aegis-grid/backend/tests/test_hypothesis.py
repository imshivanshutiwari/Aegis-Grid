from hypothesis import given, strategies as st
from main.domain.geospatial.algorithms import Haversine

@given(
    st.floats(min_value=-180, max_value=180),
    st.floats(min_value=-90, max_value=90),
    st.floats(min_value=-180, max_value=180),
    st.floats(min_value=-90, max_value=90)
)
def test_haversine_properties(lon1, lat1, lon2, lat2):
    """Property test: distance is always positive and symmetric."""
    p1 = (lon1, lat1)
    p2 = (lon2, lat2)
    dist1 = Haversine.distance(p1, p2)
    dist2 = Haversine.distance(p2, p1)

    assert dist1 >= 0
    assert abs(dist1 - dist2) < 1e-5  # Symmetry

@given(
    st.floats(min_value=-180, max_value=180),
    st.floats(min_value=-90, max_value=90)
)
def test_haversine_same_point(lon, lat):
    """Property test: distance to self is 0."""
    assert Haversine.distance((lon, lat), (lon, lat)) == 0.0
