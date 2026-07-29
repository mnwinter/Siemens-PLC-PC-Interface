"""Unit tests for first-scene JSON validation."""

from __future__ import annotations

import copy
import unittest
from pathlib import Path

from siemens_plc_pc_interface.config import load_config, parse_config
from siemens_plc_pc_interface.scene_config import (
    ConveyorPusherSceneConfig,
    SceneConfigError,
    SceneEventAction,
    load_scene_config,
    parse_scene_config,
)
from test_config import valid_config


def valid_scene_interface() -> dict:
    raw = valid_config()
    raw["version"] = 2
    raw["connection"]["cycle_ms"] = 20
    raw["points"] = [
        {
            "name": "simulated_photoeye",
            "kind": "digital",
            "tag": "pc_to_plc",
            "group": "conveyor_one",
            "inverted": False,
        },
        {
            "name": "conveyor_running",
            "kind": "digital",
            "tag": "plc_to_pc",
            "group": "conveyor_one",
            "inverted": False,
        },
    ]
    return raw


def valid_scene() -> dict:
    return {
        "version": 1,
        "physics_step_ms": 10,
        "max_catchup_steps": 5,
        "components": [
            {
                "id": "conveyor_1",
                "type": "conveyor_photoeye",
                "parameters": {
                    "length_m": 1.0,
                    "speed_m_per_s": 0.5,
                    "object_length_m": 0.2,
                    "photoeye_position_m": 0.5,
                    "minimum_photoeye_on_s": 0.1,
                },
                "bindings": {
                    "run_command": "conveyor_running",
                    "photoeye": "simulated_photoeye",
                },
            }
        ],
        "events": [
            {
                "at_ms": 0,
                "component": "conveyor_1",
                "action": "load_object",
            }
        ],
    }


class SceneConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.interface = parse_config(valid_scene_interface())

    def test_valid_scene_is_typed_and_uses_two_fixed_steps(self) -> None:
        scene = parse_scene_config(valid_scene(), self.interface)

        self.assertEqual(scene.physics_steps_per_exchange, 2)
        self.assertEqual(scene.components[0].component_id, "conveyor_1")
        self.assertIs(
            scene.events[0].action,
            SceneEventAction.LOAD_OBJECT,
        )

    def test_five_millisecond_scene_rate_is_valid(self) -> None:
        raw_interface = valid_scene_interface()
        raw_interface["connection"]["cycle_ms"] = 5
        raw_scene = valid_scene()
        raw_scene["physics_step_ms"] = 5

        scene = parse_scene_config(
            raw_scene,
            parse_config(raw_interface),
        )

        self.assertEqual(scene.plc_exchange_ms, 5)
        self.assertEqual(scene.physics_steps_per_exchange, 1)

    def test_scene_requires_typed_interface(self) -> None:
        with self.assertRaisesRegex(
            SceneConfigError,
            "interface schema version 2",
        ):
            parse_scene_config(
                valid_scene(),
                parse_config(valid_config()),
            )

    def test_physics_step_must_divide_plc_exchange(self) -> None:
        raw = valid_scene()
        raw["physics_step_ms"] = 6

        with self.assertRaisesRegex(SceneConfigError, "exact multiple"):
            parse_scene_config(raw, self.interface)

    def test_binding_ownership_is_enforced(self) -> None:
        raw = valid_scene()
        raw["components"][0]["bindings"]["run_command"] = (
            "simulated_photoeye"
        )

        with self.assertRaisesRegex(SceneConfigError, "plc_to_pc"):
            parse_scene_config(raw, self.interface)

    def test_unknown_component_type_and_event_action_are_rejected(self) -> None:
        bad_type = valid_scene()
        bad_type["components"][0]["type"] = "python.class.Name"
        with self.assertRaisesRegex(SceneConfigError, "conveyor_photoeye"):
            parse_scene_config(bad_type, self.interface)

        bad_action = valid_scene()
        bad_action["events"][0]["action"] = "run_arbitrary_code"
        with self.assertRaisesRegex(SceneConfigError, "load_object"):
            parse_scene_config(bad_action, self.interface)

    def test_event_must_align_to_fixed_physics_step(self) -> None:
        raw = valid_scene()
        raw["events"][0]["at_ms"] = 1

        with self.assertRaisesRegex(SceneConfigError, "align"):
            parse_scene_config(raw, self.interface)

    def test_pc_sensor_point_can_have_only_one_writer(self) -> None:
        raw = valid_scene()
        duplicate = copy.deepcopy(raw["components"][0])
        duplicate["id"] = "conveyor_2"
        raw["components"].append(duplicate)

        with self.assertRaisesRegex(SceneConfigError, "one component writer"):
            parse_scene_config(raw, self.interface)

    def test_scene_two_pusher_examples_form_one_typed_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        interface = load_config(
            root
            / "examples"
            / "scene-2-db14-pusher-interface.json"
        )
        scene = load_scene_config(
            root / "examples" / "scene-2-conveyor-pusher.json",
            interface,
        )

        component = scene.components[0]
        self.assertIsInstance(component, ConveyorPusherSceneConfig)
        self.assertEqual(
            component.binding.extend_command_point,
            "pusher_extend",
        )
        self.assertEqual(
            component.binding.pc_point_names,
            (
                "part_at_pusher",
                "pusher_extended",
                "pusher_retracted",
            ),
        )


if __name__ == "__main__":
    unittest.main()
