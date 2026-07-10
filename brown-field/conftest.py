"""pytest ルート設定。

テストは既存規約 `from brown.tests.conftest import create_room` でヘルパを取得するため、
本プロジェクトディレクトリを `brown` パッケージとして解決できるようエイリアスを登録する。
併せてワークスペースルートを sys.path に加え、`app` パッケージを import 可能にする。

既存テストのソースは一切変更せず、この規約を成立させるための追加設定。
"""
import os
import sys
import types

_here = os.path.dirname(os.path.abspath(__file__))

# `app` を top-level で import 可能にする。
if _here not in sys.path:
    sys.path.insert(0, _here)

# `brown` を本ディレクトリへのパッケージエイリアスとして登録し、
# `brown.tests.conftest` を tests/conftest.py に解決させる。
if "brown" not in sys.modules:
    _brown = types.ModuleType("brown")
    _brown.__path__ = [_here]
    sys.modules["brown"] = _brown
