# BCHS FRC Team 2386 COTS Library

A BCHS robotics edition of the FRC COTS add-in for Autodesk Fusion. Browse commercial off-the-shelf robot parts, insert them into an assembly, and create rigid joints without leaving the design workspace.


## Features

- Browse folders in a Fusion cloud project named `FRC_COTS`.
- Search part names, keep favorites, and view downloaded thumbnails.
- Insert `.f3d` parts and align rigid joints to supported faces, edges, or joint origins.
- Insert dynamic spacers with a chosen length or an extent to another object.
- Switch between light and dark themes.
- Supports Windows and macOS through Fusion's Python add-in environment.

## Installation

1. Install and sign in to a school-approved Autodesk Fusion installation.
2. Obtain a copy of this edition. Extract or copy the complete project to a permanent folder named **`FRC-COTS`**. A repository download may use a different folder name; rename the installation copy.
3. Keep `FRC-COTS.py`, `FRC-COTS.manifest`, `config.py`, `database_thread.py`, `frc_cots_palette.html`, `team_5000_logo.png`, `commands/`, `lib/`, and `resources/` together. `spacers/` contains optional example designs.
4. In Fusion, open **Utilities → Add-Ins → Scripts and Add-Ins**. On the **Add-Ins** tab, use **+** to select the `FRC-COTS` folder, then select the add-in and click **Run**. Fusion's labels can vary by release.
5. Leave **Run on Startup** off during initial testing; it is off in the manifest.
6. In the current Fusion hub, create or obtain access to a cloud project named **`FRC_COTS`**, with `.f3d` parts in its folders. If there are duplicate project names, the first matching accessible project is used.
7. Open an **Assembly** design (recommended for robot assemblies). In its Assembly tab's Insert panel, select **FRC COTS Library**. The library also remains available in the Hybrid Design workspace's Insert panel.

The add-in uses Python and `adsk` modules provided by Fusion. No separate Python installation, pip packages, database server, API key, or background service is required.

The folder-selection method avoids differences in default add-in locations between Fusion installations. See Autodesk's [installation guidance](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-install-an-ADD-IN-and-Script-in-Fusion-360.html) and [add-in manager guidance](https://help.autodesk.com/cloudhelp/ENU/Fusion-Model/files/SLD-MANAGE-SCRIPTS-ADD-INS.htm).

## Library and usage

An example cloud library:

```text
FRC_COTS/
  Motors/
    Kraken_X60.f3d
  Bearings/
    6804.f3d
  Spacers/
    Hex_Spacer.f3d
```

Select a supported face, edge, or joint origin, then choose a part. Review placement, flip, offsets, and other command options before accepting. Regular parts default to external references (`DEFAULT_TO_LINKED_PARTS = True`). In Assembly designs, **Link Part** stays checked because Assembly requires external components. In Hybrid designs, you can explicitly uncheck it to insert an independent copy. The checkbox starts checked for each insertion; its state is not saved.

Dynamic spacers in Assembly designs insert as linked parts at their saved length. For a custom length, prepare and save a separate Part design, add it to the library, then insert that linked part. The existing dynamic spacer length/extent dialog remains available in Hybrid designs and creates an unlinked copy. The add-in does not change a design to Hybrid automatically. Part designs cannot contain inserted components. Save the design through Fusion after checking it.

For a dynamic spacer, create a short spacer or shaft with planar end faces and a joint origin at one end, pointing outward. Use **FRC_COTS Make Spacer** in Utilities to set the spacer attribute. Hide construction origins and save the library design. The bundled `spacers/` files are examples to upload manually if needed.

## Local data and student use

The default cache is **`~/FRC-COTS_db`** (`%USERPROFILE%\FRC-COTS_db` on Windows):

- `parts_db.json`: project name/ID, part names/IDs, folder paths, versions, timestamps, and local thumbnail paths.
- `FRC_COTS_favorites.json`: part IDs and favorite flags.
- `icons/*.png`: Fusion part thumbnails.

The palette stores its theme in Fusion's embedded browser local storage under `frcCotsTheme`. Cache files are ordinary, unencrypted JSON and PNG files. Stopping or uninstalling the add-in does not remove them. A cache older than 14 days triggers an index rebuild and thumbnail deletion; this is not a comprehensive retention policy.

Read the [school IT deployment and support guide](INSTALLATION_AND_STUDENT_SAFETY.md) before classroom deployment. It covers installation requirements, administrator access, network considerations, and potential student-information exposure. The guide is supplied in Markdown format.

## Credits and license

BCHS FRC Team 2386 edition of FRC COTS. Original project: Logan de Laar, FRC Team 5000 — The Hammerheads, Hingham High School. Distributed under the [MIT license](LICENSE); Autodesk utility notices are preserved in `lib/fusionAddInUtils/`.

This edition has received source inspection and static checks. Fusion runtime behavior and compatibility must be verified on the school's Windows/macOS installations before rollout.
