
## Context-aware directions
Inspired by ChatGPT using the following prompt:

```
You are a farmer in the pre-industrial fields surrounding a settlement. Provide three sets of complex and obscure directions to a local inn, workshop or other minor landmark. Make use of features or the surrounding, diverse countryside and the rich details within the settlement
```

Result:

> Certainly! Here are three sets of complex and obscure directions to a local inn called "The Old Oak Tavern," which is a common meeting place for locals and travelers alike.
> 
> ### Directions 1: Through the Forest and Along the Brook
> 1. **Begin at the Old Mill:** Start at the Old Mill by the river's edge, where the wheel creaks with the flow of the water.
> 2. **Follow the Deer Path:** Take the narrow deer path leading into the Greenwood Forest. Keep your eye out for the ancient oak with the hollow trunk—it's a sign you're on the right path.
> 3. **Cross the Stone Bridge:** After about a mile, you'll come upon a small stone bridge crossing a babbling brook. Cross it and turn left immediately after the bridge.
> 4. **Pass the Fairy Ring:** Continue until you reach a clearing with a ring of mushrooms. Veer right here, and you'll find a barely visible trail.
> 5. **Reach the Whispering Pines:** Follow this trail until you encounter a grove of tall, whispering pines. Listen for the rustling leaves—it will guide you to the edge of the forest.
> 6. **Exit at the Cornfield:** The trail ends at the edge of a vast cornfield. Walk straight through the rows until you see a scarecrow with a red hat.
> 7. **Find the Split Oak:** Beyond the scarecrow, there stands a split oak tree. From there, the Old Oak Tavern will be visible to the northeast, just a short walk away.
> 
> ### Directions 2: Over the Hills and By the Ruins
> 1. **Start at the Village Well:** From the village well in the center of town, head west towards the rolling hills.
> 2. **Climb the Steep Hill:** Ascend the steep hill marked by the lone cedar at its peak. As you reach the top, pause to catch your breath and take in the view of the valley below.
> 3. **Descend into the Valley:** Follow the slope down into the valley, keeping the setting sun to your right. You'll pass a cluster of wild berry bushes.
> 4. **Navigate the Rocky Outcrop:** Upon reaching a rocky outcrop, look for the narrow crevice between the boulders. Squeeze through and continue on the faint path beyond.
> 5. **Pass the Ruins:** Soon, you will come across the old ruins of a watchtower, now overgrown with ivy. Circle around it to the left.
> 6. **Find the Hidden Spring:** From the ruins, head north until you find a hidden spring with crystal-clear water. Refill your canteen here if you need.
> 7. **Enter the Orchard:** Beyond the spring lies an abandoned orchard. Traverse through the gnarled apple trees until you emerge on the far side, where the Old Oak Tavern stands in plain view.
> 
> ### Directions 3: Along the River and Through the Marsh
> 1. **Begin at the Fisherman's Dock:** Start from the fisherman's dock at the riverbank, where the boats are moored and nets hang to dry.
> 2. **Follow the Riverbank:** Walk upstream along the riverbank, keeping an eye out for the giant willow tree bending over the water.
> 3. **Find the River Fork:** After a quarter mile, the river forks. Take the left fork and continue along the narrower stream.
> 4. **Enter the Marsh:** Soon, the terrain becomes marshy. Step carefully on the raised wooden planks that locals have laid down to navigate the bog.
> 5. **Locate the Marsh Lantern:** Look for the old lantern hanging from a dead tree at the marsh’s edge. This marks the transition from marshland to firmer ground.
> 6. **Traverse the Meadow:** Beyond the marsh, you'll find a wide meadow filled with wildflowers. Cross it diagonally, aiming for the stone cairn in the distance.
> 7. **Reach the Inn:** Once you reach the cairn, the Old Oak Tavern is just beyond, its sign swinging gently in the breeze.
> 
> These detailed directions should lead you through the varied and picturesque landscape to the cozy haven of the Old Oak Tavern.

#### Analysis
- Start/Begin at the {landmark} by the {natural feature}
- Take the {route} leading into {area}.
- Keep your eye out for {landmark} — it's a sign you're on the right path.
- After about {distance}, you'll come upon a {bridge} crossing a {route/natural feature}.
- Cross it (the {bridge}) and turn {body-relative direction} immediately after the bridge.
- Continue until you reach {landmark}. Veer {body-relative direction} here, and you'll find a {route}.
- Follow this trail until you encounter {landmark}.
- ~ The {path} ends at {landmark}. Walk {body-relative direction} through the rows until you see {nook feature}.
- ~ Beyond the scarecrow, there stands a split oak tree. From there, the Old Oak Tavern will be visible to the northeast, just a short walk away.

### Direction
- [ ] Cardinal: "Go northeast till {landmark}"; Based on current and target coordinates. Landmark must be along the route
- [ ] Body relative direction: "turn right at the {landmark}"