import unittest
from timeit import timeit
from game import place_ship_on_board, reset_game_state, ships

class TestGameLogic(unittest.TestCase):

    def setUp(self):
        reset_game_state()
        self.test_ship = {
            "size": (2, 1),
            "placed": False,
            "cells": [],
        }

    def test_place_valid_ship(self):
        result = place_ship_on_board(self.test_ship, (3, 3))
        self.assertTrue(result)
        self.assertTrue(self.test_ship["placed"])
        self.assertEqual(len(self.test_ship["cells"]), 2)

    def test_place_out_of_bounds_ship(self):
        result = place_ship_on_board(self.test_ship, (9, 9))
        self.assertFalse(result)

    def test_place_overlapping_ship(self):
        place_ship_on_board(self.test_ship, (2, 2))
        another = {
            "size": (2, 1),
            "placed": False,
            "cells": [],
        }
        result = place_ship_on_board(another, (2, 2))
        self.assertFalse(result)

    def test_place_too_close_ship(self):
        place_ship_on_board(self.test_ship, (2, 2))
        another = {
            "size": (2, 1),
            "placed": False,
            "cells": [],
        }
        result = place_ship_on_board(another, (3, 2))
        self.assertFalse(result)

    def test_place_ship_performance(self):
        duration = timeit(lambda: place_ship_on_board(
            {"size": (1, 1), "placed": False, "cells": []}, (0, 0)), number=1000)
        self.assertLess(duration, 0.1)

if __name__ == '__main__':
    unittest.main()
