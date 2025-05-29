""" test the utils module """

__author__ = "Andreas Werdich"
__copyright__ = "Core for Computational Biomedicine at Harvard Medical School"
__license__ = "CC0-1.0"

from cadence.utils import GroupFaker

def test_group_faker():
    """
    Create and test a fake research group using GroupFaker.
    :return: None
    """
    n_members = 9
    n_groups = 2
    gf = GroupFaker(n_members=n_members,
                    n_groups=n_groups)
    my_group = gf.create_fake_research_group()
    assert my_group.shape == (n_members, 4)