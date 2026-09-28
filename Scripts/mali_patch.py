#!/usr/bin/env python3
"""Aplica as modificações Mali no código do DXVK durante o build (CI)."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def patch(path, anchor, new, mode="after"):
    target = ROOT / path
    text = target.read_text(encoding="utf-8")

    if text.count(anchor) != 1:
        sys.exit("ERRO: ancora nao encontrada (ou repetida) em %s:\n%s" % (path, anchor))

    if mode == "after":
        text = text.replace(anchor, anchor + new)
    elif mode == "before":
        text = text.replace(anchor, new + anchor)
    else:  # "replace"
        text = text.replace(anchor, new)

    target.write_text(text, encoding="utf-8")
    print("patch ok:", path)


# Patch 1 (diagnostico): lista TODAS as features obrigatorias ausentes no log.
patch(
    "src/dxvk/dxvk_device_info.cpp",
    'return std::string("Device does not have a graphics queue");\n',
    '''
    // [MALI] lista TODAS as features obrigatorias ausentes
    for (const auto& f : getFeatureList()) {
      if (f.featureRequired && !(*f.featureEnabled))
        Logger::warn(str::format("[MALI] missing: ", f.readableName, " ",
          f.extensionEnabled ? static_cast<const char*>(f.extensionEnabled->extensionName) : "core"));
    }
''',
)
