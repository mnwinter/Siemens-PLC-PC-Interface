"""Coverage and safety tests for the symbolic native asset control catalog."""

from __future__ import annotations

import unittest

from tools.native_asset_catalog import (
    ASSET_CONTROL_BY_TYPE,
    ASSET_CONTROL_CONTRACTS,
    CATALOG_ITEMS,
    search_asset_catalog,
    validate_asset_control_catalog,
)
from tools.native_asset_library import ASSET_BY_TYPE


class NativeAssetControlCatalogTests(unittest.TestCase):
    def test_every_renderable_asset_has_one_contract(self) -> None:
        validate_asset_control_catalog()
        self.assertEqual(set(ASSET_BY_TYPE), set(ASSET_CONTROL_BY_TYPE))
        self.assertEqual(len(ASSET_CONTROL_CONTRACTS), len(ASSET_BY_TYPE))

    def test_contracts_are_symbolic_and_directional(self) -> None:
        for contract in ASSET_CONTROL_CONTRACTS:
            for point in (*contract.commands, *contract.feedback):
                with self.subTest(asset=contract.asset_type, point=point.name):
                    self.assertIn(point.type, {"BOOL", "INT", "REAL"})
                    self.assertIn(point.direction, {"PLC -> plant", "plant -> PLC"})
                    self.assertNotRegex(
                        point.name.lower(),
                        r"%[iq]|(^|_)(db|offset|ip|address)($|_)",
                    )

    def test_major_assets_expose_useful_closed_loop_points(self) -> None:
        for asset_type in ("motor", "conveyor", "pump", "fan", "tank", "machine"):
            contract = ASSET_CONTROL_BY_TYPE[asset_type]
            self.assertTrue(contract.feedback, asset_type)
            if asset_type not in {"tank"}:
                self.assertTrue(contract.commands, asset_type)

    def test_catalog_is_searchable_by_family_and_category(self) -> None:
        self.assertEqual(len(CATALOG_ITEMS), 50)
        self.assertEqual(
            {item.asset_type for item in search_asset_catalog("conveyor")},
            {
                "conveyor",
                "beltConveyor",
                "palletConveyor",
                "conveyorTurntable",
                "verticalLift",
                "diverterArm",
            },
        )
        self.assertEqual(
            {item.asset_type for item in search_asset_catalog(category="safety")},
            {"safetyFence", "safetyGate", "lightCurtain"},
        )

    def test_new_actuated_assets_have_commands_and_feedback(self) -> None:
        for asset_type in (
            "gearedMotor",
            "beltConveyor",
            "palletConveyor",
            "pneumaticCylinder",
            "parallelGripper",
            "hopper",
            "silo",
            "safetyGate",
            "controlPanel",
            "vfdCabinet",
        ):
            contract = ASSET_CONTROL_BY_TYPE[asset_type]
            self.assertTrue(contract.commands, asset_type)
            self.assertTrue(contract.feedback, asset_type)


if __name__ == "__main__":
    unittest.main()
