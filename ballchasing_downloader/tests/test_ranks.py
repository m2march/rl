from ballchasing_downloader import ranks
from ballchasing_downloader.ranks import Category

def test_parsing():
    assert (ranks.NumericRank(Category.Bronze, 2, 3) == 
            ranks.NumericRank.from_string('Bronze II Division 3'))
    assert (ranks.NumericRank(Category.Diamond, 3, 4) == 
            ranks.NumericRank.from_string('Diamond III Division 4'))
    assert (ranks.NumericRank(Category.GrandChampion, 1, 1) == 
            ranks.NumericRank.from_string('Grand Champion'))


class TestComparison():

    def test_dif_rank(self):
        Bronze = ranks.NumericRank(Category.Bronze, 1, 3)
        BronzeH = ranks.NumericRank(Category.Bronze, 3, 4)
        Silver = ranks.NumericRank(Category.Silver, 1, 3)

        assert Bronze < Silver
        assert Bronze < BronzeH 
        assert BronzeH < Silver 
        assert Silver > Bronze
        assert Silver > BronzeH

    def test_same_rank(self):
        SilverA = ranks.NumericRank(Category.Silver, 2, 2)
        SilverB = ranks.NumericRank(Category.Silver, 3, 2)
        SilverC = ranks.NumericRank(Category.Silver, 3, 3)

        assert SilverA < SilverB
        assert SilverB > SilverA
        assert SilverB < SilverC
        assert SilverC > SilverB

    def test_gc(self):
        BronzeH = ranks.NumericRank(Category.Bronze, 3, 4)
        Silver = ranks.NumericRank(Category.Silver, 1, 3)
        Champ = ranks.NumericRank(Category.Champion, 3, 3)
        GC = ranks.NumericRank(Category.GrandChampion, 1, 1)

        assert GC == max([BronzeH, Silver, Champ, GC])

    def test_unranked(self):
        BronzeH = ranks.NumericRank(Category.Bronze, 3, 4)
        Silver = ranks.NumericRank(Category.Silver, 1, 3)
        Champ = ranks.NumericRank(Category.Champion, 3, 3)
        GC = ranks.NumericRank(Category.GrandChampion, 1, 1)
        Unr1 = ranks.Unranked()
        Unr2 = ranks.Unranked()

        all_ranks = [BronzeH, Silver, Champ, GC]
        assert all([r != Unr1 for r in all_ranks])
        assert all([r != Unr2 for r in all_ranks])
        assert Unr1 == Unr2
