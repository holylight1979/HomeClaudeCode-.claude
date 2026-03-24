---
name: unity-prefab-workflow
description: SOP for programmatic WndForm/Widget prefab creation — from JSON spec to validated YAML
type: reference
---

## Prefab 程式化建立 SOP

### 工具鏈

| Tool | Path | 用途 |
|------|------|------|
| unity-yaml-tool.py | `~/.claude/tools/unity-yaml-tool.py` | generate-ui-prefab / validate / generate-meta |
| ClaudeEditorHelper.cs | `sgi_client/client/Assets/Editor/ClaudeEditorHelper.cs` | AutoGenUICode / ValidatePrefab (batch mode) |
| unity_batch.py | `~/.claude/tools/unity-desktop/unity_batch.py` | 執行 Unity batch method |

### Step 1: 設計 JSON Spec

```json
{
  "name": "WndForm_XXX",
  "children": [
    {"name": "Load_Title", "type": "Text", "anchor": "top-center", "size": {"x": 600, "y": 60}},
    {"name": "Confirm", "type": "UIButtonCustom", "anchor": "bottom-center", "size": {"x": 200, "y": 60}},
    {"name": "Scroller", "type": "Scroller", "anchor": "stretch", "scroll_class": "XXXScroller"}
  ]
}
```

**支援的 child type**: Text, Image, UIButtonCustom, Scroller, Empty
**支援的 anchor preset**: stretch, top-left, top-center, top-right, center, bottom-center, ...（共 14 種）

### Step 2: 生成 Prefab + Meta

```bash
python unity-yaml-tool.py generate-ui-prefab spec.json Assets/Res/UI/WndForm/WndForm_XXX.prefab
python unity-yaml-tool.py generate-meta Assets/Res/UI/WndForm/WndForm_XXX.prefab.meta --importer PrefabImporter
```

### Step 3: 靜態驗證

```bash
python unity-yaml-tool.py validate Assets/Res/UI/WndForm/WndForm_XXX.prefab
```

檢查：fileID 交叉引用、m_Script 非零、m_GameObject 引用

### Step 4: Unity 在線驗證（需關閉 Unity Editor）

```bash
python unity_batch.py -p sgi_client/client -m ClaudeEditorHelper.RefreshAssets
python unity_batch.py -p sgi_client/client -m ClaudeEditorHelper.ValidatePrefab --extra-args "-prefab Assets/Res/UI/WndForm/WndForm_XXX.prefab"
```

如果 Unity Editor 已開啟：切回 Unity → 會自動 Refresh → 檢查 Console 是否有紅字

### Step 5: AutoGenUICode

```bash
python unity_batch.py -p sgi_client/client -m ClaudeEditorHelper.AutoGenUICode --extra-args "-prefab Assets/Res/UI/WndForm/WndForm_XXX.prefab"
```

產出：InitComp.cs + UIEvent.cs

### 注意事項

- Root 自動建立 6 元件：RectTransform + Canvas + GraphicRaycaster + CanvasGroup + UIPerformance + ILUIWnd
- RefDb 自動從 children 建立，_key = child name, _typeName = child type
- Scroller 需要 3 元件：EnhancedScroller + ILUIScrollerController（在同一 GO）
- ScrollerCell widget 需要另外建立
- 所有 UI 物件 m_Layer = 5（UI layer）
