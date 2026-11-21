"""Herinnering 28 nov 2026 (eigenaar 21 nov): cijfers vergelijken voor Sleep Archives en BlackswanVault, één seintje per kanaal (ntfy)."""
import sys
sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
import swan_yt_wacht as w
w.seintje("Sleep Archives: cijfers vergelijken",
          "Vandaag vergelijken met de nulmeting (stories/CIJFERS-NULMETING.md): CTR, gem. weergaveduur, % na 1 minuut. "
          "Open Claude en plak het overzicht uit YouTube Studio.")
w.seintje("BlackswanVault: cijfers vergelijken",
          "Vandaag vergelijken met de beginstand (24 okt - 20 nov): weergaven, kijkuren lange video's, CTR. "
          "Open Claude en plak het overzicht uit YouTube Studio.")
