from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

# Make sure shared/ is importable so "core.*" works
BASE = Path(__file__).resolve().parents[1]          # .../apps/debt_calculator
sys.path.insert(0, str(BASE / "shared"))

import core.storage as storage
import core.data_access as data_access
import core.profiles as profiles


def base_dir() -> Path:
    """
    Web data location.
    NOTE: Streamlit Cloud file system is not permanent across redeploys; good for dev/testing.
    """
    p = BASE / "web" / ".data"
    storage.ensure_dir(p)
    return p


def profiles_index_path() -> Path:
    return base_dir() / "profiles_index.json"


def load_profiles_index() -> Dict[str, Any]:
    idx_path = profiles_index_path()
    idx = profiles.ensure_default_profile(idx_path)  # creates default + active_profile_id if missing
    return idx


def set_active_profile(profile_id: str) -> None:
    idx_path = profiles_index_path()
    idx = profiles.load_profiles_index(idx_path)
    idx["active_profile_id"] = profile_id
    profiles.save_profiles_index(idx_path, idx)


def get_active_profile() -> profiles.Profile:
    idx = load_profiles_index()
    return profiles.get_active_profile(idx)


def list_profiles() -> list[profiles.Profile]:
    idx = load_profiles_index()
    return profiles.list_profiles(idx)


def add_profile(name: str) -> None:
    idx_path = profiles_index_path()
    idx = profiles.load_profiles_index(idx_path)
    profiles.add_profile(idx_path, idx, name)


def rename_profile(profile_id: str, new_name: str) -> None:
    idx_path = profiles_index_path()
    idx = profiles.load_profiles_index(idx_path)
    profiles.rename_profile(idx_path, idx, profile_id, new_name)


def delete_profile(profile_id: str) -> None:
    idx_path = profiles_index_path()
    idx = profiles.load_profiles_index(idx_path)
    profiles.delete_profile(idx_path, idx, profile_id)


def load_section(section: str) -> Dict[str, Any]:
    p = get_active_profile()
    data_access.ensure_profile_dirs(base_dir(), p.id)
    data = data_access.load_profile_data(base_dir(), p.id)
    return data.get(section, {})


def save_section(section: str, payload: Dict[str, Any]) -> None:
    p = get_active_profile()
    data_access.ensure_profile_dirs(base_dir(), p.id)
    data_access.save_profile_section(base_dir(), p.id, section, payload)
