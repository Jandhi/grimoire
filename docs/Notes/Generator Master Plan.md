
## Hierarchies
In principle, there should be two separate ways of dividing the build area: Geographical and sociopolitical areas.

```mermaid
flowchart TD

hierarchies(Area hierarchies)

geographical(Geographical areas)
expanse([1: Expanse])
biome([2: Biome])
region([3: Region])

sociopolitical(Sociopolitical areas)
territory([1: Territory])
county([2: County])
district([3: District])
block([4: Block])
plot([5: Plot])
subplot(["(optional 6+: Sub-Plots)"])

hierarchies -.- geographical & sociopolitical

geographical -.- expanse ==> biome ==> region

sociopolitical -.- territory ==> county ==> district ==> block ==> plot --> subplot --> subplot

```
On the geographical side:
- Expanses: The expanses fill the areas up to natural barriers (e.g. of a deep river or mountain range).
- Biome areas: The biome areas fill each contiguous area of the same biome, up to the edge of the expanse.
- Regions: Sub-divisions of the biome areas based on the contents (think of this like sub-biomes), or as a means of dividing a largely featureless area into smaller parts.

And, based on the geography:
- Territories: The territories are a contiguous collection of regions within the same expanse, which are either suitable or unsuitable for habitation. Each territory suitable for habitation could spawn one or multiple settlements of the same culture/nation/ethnicity/... .
- Counties: The counties are contiguous collections of regions (typically of the same biome) within the same territory, and are generally either rural or urban. These often form some kind of community, with distinct cultural or architectural differences that still have elements in common with the other counties of their territory.
- Districts: Within each county, the space is further subdivided into areas of specialty. From this level down, more or less emphasis may be placed on geographical areas, and terraforming may take place. Rural places might differentiate between farmland, forests, and villages for example; while urban areas might have different wealth or industry across different districts.
- Blocks: Blocks are a sub-division of districts which may even further specialise, or just cause further grouping within the district to aid navigability.
- Plots: Plots are distinct areas of land that are designated for a specific purpose or structure, such as housing or other buildings, features, or for greenery.
- Sub-plots: Optionally, a plot may decide to further dub-divide itself, but these subdivisions are't typically visible for any higher levels of the hierarchy. The plot acts as the smallest area of interest, but sub-plots may cause modifications to the properties of the plot (for example, allowing other systems to differentiate a park with a playground or pond from one that does not have these features).


## Generative process

The process generally follows the sequence of
1. Initialise: Set up generator and its starting parameters.
2. Analyse: Inspect the geography, creating geographical areas and synthesising information on the build area. A top-down process. In this phase, certain areas of the build region may be ignored for further analysis as a means of optimisation.
3. Plan: Consolidate the regions into sociopolitical areas, and impose constraints on the next-lower level. A top-down process.
4. Build: Decide what to build based on the constraints, and propagate the decision to the next-higher level to aid feature coordination. List optional or optimisation tasks to be completed later. A buttom-up process.
5. Polish: Pick up optional or optimisation tasks based on priority to fill the remaining time. A chaotic process.

```mermaid
flowchart TD

start((Start))

initial(Initialise)
analysis(Analyse)
planning(Plan)
building(Build)
polishing(Polish)

done((Done!))

start --> initial --> analysis --> planning --> building --> polishing --> done

a-expanses(Establish expanses: Identify natural barriers, and create expanses for the areas between them.)
a-biomes(Establish biome areas: Divide each Expanse into its biomes.)
a-regions("Establish regions: Using a weighted Voronoi or by identifying special features (e.g. varying density of trees), create geographic regions which are internally consistent (e.g. a flower field, a mountain plateau, ...)")

analysis --> a-expanses --> a-biomes --> a-regions --> analysis

p-territories(Establish territories: Distribute the regions into territories.)
p-counties(Establish counties: Within each territory, group the regions into separate communities.)
p-districts("Establish districts: Separate each county into districts which each braodly cover a function (e.g. housing, entertainment, commerce...). Multiple districts of the same type may occur. Terraforming may be applied at this level.")
p-blocks("Establish block: Separate each district into blocks which designate an area for use for a more specific use (e.g. in park: pond, picnic space, public amenities etc.). Terraforming may be applied at this level.")
p-plots(Establish plots: Separate each block into rectangular plots. Plots are given a specific functions. Terraforming may be applied at this level.)
p-networks(Establish networks: Plan all networks, such as paths, sewers, etc., as far as possible.)
p-cleanup(Clean-up: Update all regions to reflect relevant information, such as no-build zones reserved by networks, or connection points to networks.)

planning --> p-territories --> p-counties --> p-districts --> p-blocks --> p-plots --> p-networks --> p-cleanup --> planning

b-networks(Build networks: E.g. paths, up to their connection points.)
b-plots(Build plot features: E.g. houses.)
b-blocks(Build block features: E.g. courtyards.)
b-districts(Build district features: E.g. street furniture.)
b-counties(Build county features: E.g. city walls.)
b-territories(Build territorial features: E.g. border checkpoints or battlefields.)

building --> b-networks --> b-plots --> b-blocks --> b-districts --> b-counties --> b-territories --> building


```

## Repository Structure

Each feature should be able to provide results for planning and building, and may also return optional callables as a result of building, which may be executed during the polishing phase.
```mermaid
flowchart TD

root(/ - The repository root) --> README.md & LICENSE & grimoire & docs & tests

docs(/docs - Where we put all our documentation)

tests(/tests - Where we put all our testing code)

grimoire(/grimoire - The package which is our generator) --> library & utilities & generator & CLI-main & main

CLI-main("/_ _ main _ _.py - The CLI wrapper for main.py.")

main("/main.py - The generator itself.")

library("/library - Where we put all assets and resources.")

utilities("/utilities - Where we put all generalised functionality which is used across multiple areas (and could potentially be ported to GDPC).")


generator("/generator - Where we put all the code specific to our generator.") --> management & supplemental & features


management("/management - All code that controls the flow and data of the generator") --> interfaces & models & controls

interfaces(/interfaces - All interfaces to third-party code and the user, e.g. GDPC, Matplotlib, CLI and logging.)
models(/models - All classes that are used throughout the generator.)
controls(/controls - All generic functions used in decision-making and resource management, including randomness and utility functions.)

features("/features - All the code that relates to specific physical structures or features, including buildings, infrastructure and decoration.") -.-> feature1 & feature2

feature2(["/feature2.py - Example feature which can be contained in a single file."])
feature1(["/feature1 - Example feature which is more complex. Thanks to the init file, it can be called identically to feature1."]) --> init("_ _ init _ _.py") & subfeature1.py & subfeature2

supplemental("/supplemental - All code which may be applied either at any time during the process, is optional, or can run indefinitely.")

```
