# Assembly and linked-part regression checks

Run the automated checks outside Fusion:

```sh
python3 -m unittest discover -s tests -v
```

These checks import the add-in with Fusion API doubles. They verify toolbar registration, design-intent routing, linked defaults and enforcement, explicit Hybrid copies, and failed linked insertion. They do not verify Fusion's native insertion, joint creation, or toolbar rendering.

Before distributing an installation package, test in the current school-approved Fusion version with disposable designs and an accessible `FRC_COTS` project:

1. Start the add-in and open an Assembly design. Confirm **FRC COTS Library** appears in the Assembly tab's Insert panel.
2. Select a supported placement face, edge, or joint origin and insert a regular part. Confirm **Link Part** is checked and disabled, placement and offsets work, and the resulting component is an external reference. Save, reopen, and verify the reference remains intact.
3. Update a test library source, save it, then retrieve its update in the assembly through Fusion. Confirm the linked component updates.
4. Insert a dynamic spacer into an Assembly design. Confirm it inserts as a linked component at the source's saved length without a geometry-resizing command or a design-intent conversion.
5. Open a Hybrid design. Confirm the library button is available, regular parts start linked, and explicitly unchecking **Link Part** inserts an independent copy. Confirm the next insertion starts linked again. Check existing dynamic spacer sizing and placement.
6. Try insertion in a Part design. Confirm the add-in explains that an Assembly or Hybrid design is required.
7. Test a source that Fusion cannot reference, such as an inaccessible source or a restricted project relationship. Confirm the command fails without inserting an unlinked replacement.
8. Stop and restart the add-in. Confirm its toolbar buttons are removed and restored without duplicates.
