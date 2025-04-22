# IBL-Importer v0.1

## About
IBL Importer is a tool I'm developing on my free time and is compatible with Maya (2023+) and Houdini (19.0+). 

It uses MongoDB as the database behind it and can be easily adapted to any workflow.

It has also been proven extremely useful and successful in Production Environments, by being used by artists at The Flying Colour Company.

The tool has been developed out of necessity as I have hundreds of different HDRIs and Light Maps that I use for my CG Renders and manually going through files, testing in the scene, and redoing the process until I found one is extremely time consuming when you have that many files to go through.

*IBL Importer in Maya*
![unnamed (1)](https://github.com/user-attachments/assets/215af1e8-df76-4ceb-9a47-6f076d46757d)

*IBL Importer in Houdini*
![unnamed](https://github.com/user-attachments/assets/946379ee-4c1c-4aac-b1ab-cca8f1623230)

## Features

- Adds any Light Map or HDRI from the users Library to the user's scene.
- Creates a simple setup with an AiBlackBody so the user can adjust light temperature correctly. 
- Allows the user to set up Light Intensity and Exposure before importing the lights into the scene.
- Allows the user to choose how many items get loaded in at the same time on the UI.
- Sets up the correct colour space for the files in the user's shaders.

### Houdini specific: 
- Allows the user to choose between Arnold and Solaris Lights before creation of lights in the scene.
- Creates a Material Network called “LGT_Shaders” on the user's /obj section, all the light shaders will be stored here and properly connected to the light.

## Future Updates / Roadmap
- Add search function to allow users to search for specific items.
- Add a favourites section that users can use to store their favourite lightmaps.
- Create complimentary tools that help the user add, update and manage items in their Libraries easily.
- Add functionality to send assets between Nuke, Houdini and Maya in order to facilitate customisation of lightmaps.

