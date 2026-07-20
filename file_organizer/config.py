"""Configuration loading and merging for file-organizer."""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path.home() / ".file_organizer" / "config.yml"


def _read_yaml_file(path: Path, explicit: bool = False) -> Dict[str, List[str]]:
    """
    Read a YAML file and return its contents as a dict, or {} if missing/invalid.
    If explicit=True, warn when the file is missing (used for --config, where
    the user asked for this specific path, vs. the default home config which
    is optional).
    """
    if not path.exists():
        if explicit:
            logger.warning(f"--config path {path} does not exist; ignoring.")
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.warning(f"Could not parse config file {path}: {e}")
        return {}
    except (OSError, UnicodeDecodeError) as e:
        logger.warning(f"Could not read config file {path}: {e}")
        return {}

    if not data:
        return {}
    if not isinstance(data, dict):
        logger.warning(f"Config file {path} did not contain a mapping; ignoring.")
        return {}

    return _validate_extension_map(data, path)


def _validate_extension_map(data: Dict, path: Path) -> Dict[str, List[str]]:
    """
    Ensure every category maps to a list of string extensions.
    Drops malformed entries individually (with a warning) instead of
    letting them crash merge_extension_maps() later, far from the source.
    """
    cleaned: Dict[str, List[str]] = {}
    for category, extensions in data.items():
        if isinstance(extensions, str):
            logger.warning(
                f"Config file {path}: category '{category}' should be a list "
                f"of extensions, got a single string '{extensions}'. Wrapping it."
            )
            extensions = [extensions]
        elif not isinstance(extensions, list):
            logger.warning(
                f"Config file {path}: category '{category}' has an invalid "
                f"value ({extensions!r}); skipping this category."
            )
            continue

        valid_exts = []
        for ext in extensions:
            if not isinstance(ext, str):
                logger.warning(
                    f"Config file {path}: category '{category}' has a "
                    f"non-string extension ({ext!r}); skipping it."
                )
                continue
            valid_exts.append(ext)

        if valid_exts:
            cleaned[category] = valid_exts

    return cleaned


def merge_extension_maps(*maps: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Merge multiple extension maps in order (later maps take precedence).
    If the same extension appears in two categories, the later map wins.
    """
    merged: Dict[str, List[str]] = {}
    # Build it category -> set of extensions, then resolve conflicts by extension
    extension_owner: Dict[str, str] = {}  # extension -> category

    for m in maps:
        for category, extensions in m.items():
            for ext in extensions:
                ext = ext.lower()
                extension_owner[ext] = category  # later map overwrites earlier

    for ext, category in extension_owner.items():
        merged.setdefault(category, [])
        if ext not in merged[category]:
            merged[category].append(ext)

    return merged


def load_config(
    default_map: Dict[str, List[str]],
    config_path: Optional[str] = None,
    overrides: Optional[List[str]] = None,
) -> Dict[str, List[str]]:
    """
    Build the final extension map by merging, in order:
    1. default_map (your hardcoded EXTENSION_MAP)
    2. ~/.file_organizer/config.yml (if it exists)
    3. config_path, if explicitly passed (--config)
    4. overrides, a list of "ext:category" strings (--add-extension)
    """
    layers = [default_map]

    home_config = _read_yaml_file(DEFAULT_CONFIG_PATH)
    if home_config:
        layers.append(home_config)

    if config_path:
        cli_config = _read_yaml_file(Path(config_path), explicit=True)
        if cli_config:
            layers.append(cli_config)

    merged = merge_extension_maps(*layers)

    if overrides:
        override_map: Dict[str, List[str]] = {}
        for item in overrides:
            if ":" not in item:
                logger.warning(f"Ignoring malformed --add-extension value: {item}")
                continue
            ext, category = item.split(":", 1)
            override_map.setdefault(category, []).append(ext.strip())
        merged = merge_extension_maps(merged, override_map)

    return merged