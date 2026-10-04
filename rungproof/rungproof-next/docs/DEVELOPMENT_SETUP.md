# Development setup

Pin the toolchain before authoring production assets:

1. Use Godot 4.7.2 .NET for Windows.
2. Use the x64 .NET 10 SDK. Godot 4.7.2 requires its .NET 10 host runtime.
3. Use Blender 5.2.2 LTS for the pinned asset-authoring pipeline.
4. Keep downloaded tools outside source control; `.tools/` is ignored. The
   verified workstation toolchain is portable under `.tools/`.
5. Open `project.godot` with the .NET Godot editor and allow it to restore the
   `Godot.NET.Sdk/4.7.2` package.

Do not migrate primitive geometry into the production catalog. The first
accepted asset must pass `ASSET_QUALITY_STANDARD.md` from Blender source through
Godot render and blind review.

Verified local entry points:

- `.tools/dotnet/dotnet.exe`
- `.tools/godot/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64.exe`
- `.tools/blender/blender-5.2.2-windows-x64/blender.exe`

The Godot project must retain `[dotnet] project/assembly_name="RungProof.Next"`;
without it Godot searches for an assembly derived from the display name and
cannot bind the C# scene scripts.

Run `python .\tools\validate_asset_evidence.py` before any catalog promotion.
It is intentionally advisory for unfinished candidates and mandatory for every
entry admitted to `production.catalog.json`.
