"""Unit tests base for all OreSat OD databases."""

import re
import unittest

import canopen

from oresat_configs import NodeId, OreSatConfig, OreSatId
from oresat_configs._yaml_to_od import OD_DATA_TYPE_SIZE, TPDO_COMM_START, TPDO_PARA_START


class TestConfig(unittest.TestCase):
    """Base class to test a OreSat OD databases."""

    def setUp(self):
        self.id = OreSatId.ORESAT0
        self.config = OreSatConfig(self.id)

    def test_tpdo_sizes(self):
        """Validate TPDO sizes."""

        for node in self.config.od_db:
            tpdos = 0
            od = self.config.od_db[node]
            for i in range(16):
                tpdo_comm_index = TPDO_COMM_START + i
                tpdo_para_index = TPDO_PARA_START + i
                has_tpdo_para = tpdo_comm_index in od
                has_tpdo_comm = tpdo_para_index in od
                self.assertEqual(has_tpdo_comm, has_tpdo_para)
                if not has_tpdo_comm and not has_tpdo_comm:
                    continue
                mapping_obj = od[tpdo_para_index]
                size = 0
                for sub in mapping_obj.subindices:
                    if sub == 0:
                        continue
                    raw = mapping_obj[sub].default
                    mapped_index = (raw & 0xFFFF0000) >> 16
                    mapped_subindex = (raw & 0x0000FF00) >> 8
                    mapped_obj = od[mapped_index]
                    if not isinstance(mapped_obj, canopen.objectdictionary.Variable):
                        mapped_obj = mapped_obj[mapped_subindex]
                    self.assertTrue(
                        mapped_obj.pdo_mappable,
                        f"{self.id.name} {node.name} {mapped_obj.name} is not pdo mappable",
                    )
                    size += OD_DATA_TYPE_SIZE[mapped_obj.data_type]
                self.assertLessEqual(
                    size, 64, f"{self.id.name} {node.name} TPDO{i + 1} is more than 64 bits"
                )
                tpdos += 1

            # test the number of TPDOs
            if od.device_information.product_name == "c3":
                self.assertLessEqual(tpdos, 1)
            else:
                self.assertLessEqual(tpdos, 16)

    def test_beacon(self):
        """Test all objects reference in the beacon definition exist in the C3's OD."""

        length = 0

        dynamic_len_data_types = [
            canopen.objectdictionary.VISIBLE_STRING,
            canopen.objectdictionary.OCTET_STRING,
            canopen.objectdictionary.DOMAIN,
        ]

        for obj in self.config.beacon_def:
            if obj.name == "start_chars":
                length += len(obj.default)  # start_chars is required and static
            else:
                self.assertNotIn(
                    obj.data_type,
                    dynamic_len_data_types,
                    f"{self.id.name} {obj.name} is a dynamic length data type",
                )
                length += OD_DATA_TYPE_SIZE[obj.data_type] // 8  # bits to bytes

        # AX.25 payload max length = 255
        # CRC32 length = 4
        self.assertLessEqual(length, 255 - 4, f"{self.id.name} beacon length too long")

    def test_record_array_length(self):
        """Test that array/record have is less than 255 objects in it."""

        for od in self.config.od_db.values():
            for index in od:
                if not isinstance(od[index], canopen.objectdictionary.Variable):
                    self.assertLessEqual(len(od[index].subindices), 255)

    def _test_snake_case(self, string: str):
        """Test that a string is snake_case."""

        regex_str = r"^[a-z][a-z0-9_]*[a-z0-9]*$"  # snake_case with no leading/trailing num or "_"
        self.assertIsNotNone(re.match(regex_str, string), f'"{string}" is not snake_case')

    def _test_variable(self, obj: canopen.objectdictionary.Variable):
        """Test that a variable is valid."""

        self.assertIsInstance(obj, canopen.objectdictionary.Variable)
        self.assertIn(obj.data_type, OD_DATA_TYPE_SIZE.keys())
        self.assertIn(obj.access_type, ["ro", "wo", "rw", "rwr", "rww", "const"])
        self.assertIsInstance(obj.data_type, int)
        self._test_snake_case(obj.name)

        if not isinstance(obj.parent, canopen.ObjectDictionary):
            node_name = obj.parent.parent.device_information.product_name
        else:
            node_name = obj.parent.device_information.product_name

        # test variable's default value match the data type
        if obj.data_type == canopen.objectdictionary.BOOLEAN:
            self.assertIsInstance(
                obj.default,
                bool,
                f"{node_name} object 0x{obj.index:X} 0x{obj.subindex:02X} was not a bool",
            )
        elif obj.data_type in canopen.objectdictionary.INTEGER_TYPES:
            self.assertIsInstance(
                obj.default,
                int,
                f"{node_name} object 0x{obj.index:X} 0x{obj.subindex:02X} was not a int",
            )
        elif obj.data_type in canopen.objectdictionary.FLOAT_TYPES:
            self.assertIsInstance(
                obj.default,
                float,
                f"{node_name} object 0x{obj.index:X} 0x{obj.subindex:02X} was not a float",
            )
        elif obj.data_type == canopen.objectdictionary.VISIBLE_STRING:
            self.assertIsInstance(
                obj.default,
                str,
                f"{node_name} object 0x{obj.index:X} 0x{obj.subindex:02X} was not a str",
            )
        elif obj.data_type == canopen.objectdictionary.OCTET_STRING:
            self.assertIsInstance(
                obj.default,
                bytes,
                f"{node_name} object 0x{obj.index:X} 0x{obj.subindex:02X} was not a bytes",
            )
        elif obj.data_type == canopen.objectdictionary.DOMAIN:
            self.assertIsNone(
                obj.default, f"{node_name} object 0x{obj.index:X} 0x{obj.subindex:02X} was not None"
            )
        else:
            raise ValueError(f"unsupported data_type {obj.data_type}")

        self.assertEqual(obj.default, obj.value)

    def test_objects(self):
        """Test that all objects are valid."""

        for od in self.config.od_db.values():
            for index in od:
                if isinstance(od[index], canopen.objectdictionary.Variable):
                    self._test_variable(od[index])
                else:
                    self._test_snake_case(od[index].name)

                    # test subindex 0
                    self.assertIn(0, od[index])
                    self.assertEqual(od[index][0].data_type, canopen.objectdictionary.UNSIGNED8)
                    self.assertEqual(
                        od[index][0].default,
                        max(list(od[index])),
                        f"index 0x{index:X} mismatch highest subindex",
                    )

                    # test all other subindexes
                    array_data_types = []
                    for subindex in od[index]:
                        if isinstance(od[index], canopen.objectdictionary.Array) and subindex != 0:
                            array_data_types.append(od[index][subindex].data_type)
                        self._test_variable(od[index][subindex])

                    # validate all array items are the same type
                    self.assertIn(len(set(array_data_types)), [0, 1])
