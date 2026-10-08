# BCHS FRC Team 2386 COTS Library School IT Deployment and Support Guide

BCHS robotics • Version 1.3.0-2386.3 • October 8, 2026

## Purpose and assessment

This guide supports school IT in assessing, installing, piloting, and troubleshooting the BCHS FRC Team 2386 COTS Library on managed school computers. It provides deployment requirements, security and student-data considerations, common fault checks, acceptance criteria, and a support handoff. Robotics mentors can use it to supply the library and test designs; IT retains responsibility for device, account, and deployment approval.

The add-in supports student robot CAD work by browsing a parts library and inserting components. No student-record collection, analytics, advertising, or direct third-party upload functionality. Its suitability for student use depends on approved Autodesk accounts, restricted project access, protected local profiles, and a reviewed installation. 

### What the software does

A local Python add-in runs inside Fusion. A bundled HTML and JavaScript palette provides folder navigation, part-name search, favorites, thumbnails, and a light/dark theme. Fusion's API locates the first accessible project named FRC_COTS in the current project collection, reads its folders and .f3d parts, and builds a local index. Searching takes place in the palette; no separate search service is implemented.

In Hybrid designs, the add-in opens the source document temporarily to inspect its dynamic-spacer attribute, then closes it without saving. Assembly designs insert all library items through the linked-part command without this attribute inspection. Insertion changes the active CAD design: it adds components and rigid joints; spacer commands can resize geometry, create copies, and group timeline features. The Make Spacer command changes design attributes and removes existing FRC_COTS joint attributes. Users save designs through Fusion. Regular parts default to linked external references. Assembly designs require linking; Hybrid users may explicitly choose an unlinked copy. Assembly spacer insertion references the saved part at its existing length. Custom spacer lengths for Assembly must be prepared and saved in separate Part designs; the add-in does not alter the library source geometry. Dynamic spacer resizing in Hybrid continues to use unlinked copies.

### Identity and review scope

This is the BCHS FRC Team 2386 edition of FRC COTS, derived from Logan de Laar and FRC Team 5000's project. Original MIT copyright and Autodesk utility notices remain. 

The assessment covers the Python, HTML, manifest, configuration, and bundled utility code in this repository. It is a source-based assessment, not a security certification, penetration test, or approval of Autodesk's service. Fusion runtime testing, school policy review, and verification of Autodesk account and cloud settings are required before deployment. Example .f3d files require separate CAD review before use.

## Answers to common IT concerns

### Does this need administrator access or extra software

The add-in itself does not request elevation or install a service, driver, system Python, pip package, database server, or browser extension. It runs under the Fusion user's permissions. Installing Fusion, deploying files into an IT-managed location, or setting access controls may require IT administration. These are deployment tasks, not a reason to run student Fusion sessions as an administrator.


### Does this connect to school information systems

No student-information-system, email, gradebook, directory, or learning-management-system connector is implemented. The actual CAD workflow and possible incidental personal information are described in the student-information section. 

### Does this require new firewall openings

No separate add-in endpoint, inbound listener, or team server is implemented. It uses Fusion's existing cloud services through the Autodesk API. If Fusion cloud access already works, first test this add-in under the existing approved rules. 

### Is it signed or covered by a support agreement

The repository provides source and a manifest; it does not implement package-signature verification or provide evidence of vendor certification, a school support agreement, or a guaranteed response time. 


## Installation and first use

### Requirements

Use a school-approved Autodesk Fusion installation on Windows or macOS and an Autodesk account allowed to access the robotics library. The user needs read access to the add-in folder, write access to the configured cache folder, and appropriate permissions for the active design. Fusion provides Python and the adsk API modules; no separate pip dependencies, database server, API key, administrator-level service, or standalone Python installation is required by this add-in.

### Installation steps

1. Obtain the complete reviewed Team 2386 edition from the team's approved distribution location. 
2. Extract or copy it to a permanent folder named FRC-COTS. The folder name must match FRC-COTS.py and FRC-COTS.manifest. Do not select the repository's parent folder or leave a nested FRC-COTS folder inside the installation.
3. Keep these files together: FRC-COTS.py, FRC-COTS.manifest, config.py, database_thread.py, frc_cots_palette.html, team_5000_logo.png, and the commands, lib, and resources folders. The spacers folder contains optional example models. README and LICENSE should accompany the distribution.
4. Open Fusion, then Utilities > Add-Ins > Scripts and Add-Ins. Select the Add-Ins tab, use the plus button to select the FRC-COTS folder, select the add-in, and click Run. UI labels may vary by release. Leave Run on Startup off initially; the manifest defaults to false.
5. In the current Fusion hub, create or obtain access to a project named FRC_COTS. Populate it with approved .f3d parts. Subfolders become library categories. Avoid duplicate project names: selection uses the first match, not an explicitly configured project ID.
6. Open a disposable Assembly design and choose FRC COTS Library from the Assembly tab's Insert panel. Hybrid designs retain the button in their Design workspace's Insert panel. Confirm library loading, folder browsing, search, favorites, thumbnails, insertion, joints, and spacer behavior. Restart Fusion to check persisted settings.

### Configuration and updates

config.py selects the cloud project name with PARTS_DB_PROJECT. PARTS_DB_FOLDER defaults to the current user's home directory, and PARTS_DB_PATH defaults to its FRC-COTS_db subfolder. The parent must already exist. DEFAULT_TO_LINKED_PARTS is true and DEBUG is false. Assembly insertion always stays linked even if the configured default is changed; Hybrid offers an explicit opt-out. No new preference file is written to remember the checkbox. If changing cache location, use a dedicated protected folder: thumbnail refresh can delete files within its icons subfolder.

Updates are manual; no automatic updater is implemented. Stop the add-in before replacing files, keep the approved version available for rollback, and repeat the acceptance checks after updates. Do not enable startup loading until the pilot passes.

## Student information and operating safeguards

### Information the current code could expose

The code has no dedicated fields or connectors for student names, student numbers, grades, attendance, health information, accommodations, parent contacts, or school passwords. It does not request a roster or implement camera, microphone, email, or learning-management-system access.

Personal information can still appear incidentally. Student names in project names, folder names, file names, model labels, or visible CAD geometry may be displayed, cached, or included in logs. Favorites and the local profile path may identify or be associated with a user. An active design containing sensitive information is accessible to Fusion and its add-in commands. Autodesk account identity and access rights are managed by Fusion; this add-in has no separate login or password-storage feature.

### Potential access and trust boundary

The configured FRC_COTS project limits the implemented browsing workflow. It is not an enforced security boundary for an arbitrary or modified add-in. Python code runs within the Fusion process and can potentially read or modify other accessible designs, call more Fusion APIs, and access files or networks allowed to that process and user. The source does not implement an independent permission system or a read-only sandbox. Operating-system controls and Autodesk permissions must provide the access limits.

Local JSON files and thumbnails are trusted inputs to this implementation. Protect the cache against changes by other users and do not distribute someone else's cache as part of the installer. There is no built-in package signature verification, integrity monitor, or cache encryption.
