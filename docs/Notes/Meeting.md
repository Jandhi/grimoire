- [ ] Jan
	- [ ] Grid stays the same
	- [ ] Help refactor
	- [ ] Create material system
	- [ ] Integrate material system with prefabs
- [ ] Tim
	- [ ] More parameters
	- [ ] Types
- [ ] Zach
	- [ ] With Dylan discuss furnishing
	- [ ] Implement system for limited furniture
- [ ] Victor
	- [ ] Road models
		- [ ] Direction vectors
	- [ ] Good placement on light posts
	- [ ] Signposting
	- [ ] Dry walls
- [ ] James
	- [ ] Clean up refactors
	- [ ] Finish erode tests
	- [ ] Identify spare 
- [ ] Dylan
	- [ ] Rewrite path generation

# Debriefing

Goals and milestones for this year:

- [ ] No stress (limited scope, plan for interruption/early finish)
	- [ ] No shame in "handing off" responsibility or asking for help
	- [ ] Major systems which were added too late to review
		- [ ] Feature branches became too big > lead to major bugfix stress post-integration
	- [ ] Overambitious
		- [ ] (Estimate task duration)
		- [ ] Separate into smaller subtasks
		- [ ] Defining "requirements"
	- [ ] PRs sat around for a long time
		- [ ] PRs no longer than a week
		- [ ] More robust testing
			- [ ] Solid testing concept
			- [ ] Modular testing
		- [ ] Smaller PRs
			- [ ] Specific features, not whole systems
			- [ ] Start with absolute minimal feature (requirements engineering)
		- [ ] More involvement
			- [ ] Pair reviews (improve understanding)
	- [ ] Clean separation of production and debug code
- [ ] Spend at least 2 hours a week per person on the project (>20h/person)
	- [ ] Not very helpful
- [ ] 2x two-week development sprints with retro and planning
	- [ ] Clearer/more structured meetings
		- [ ] Dates and times defined early
		- [ ] List of meeting objectives (typical and special)
- [ ] 1 week for polish
	- [ ] Is important, and should be prioritised
	- [ ] If something takes more than one sprint, send backup
- [ ] Document and share at least 1 module with the community (post-competition)
	- [ ] Materials
		- [ ] Design review
	- [ ] Nooks
		- [ ] Implement "nested"/district Nooks
		- [ ] Design review
- [ ] Weekly updates in the community?
	- [ ] At opportune moments, weekly doesn't make sense

## Further Discussion
### Goals
- [ ] Get more familiarity
	- [ ] ! System architecture > @james
- [ ] Get a score greater than 4.25, 4.75, 4.5, and 5.5 in adaptability, functionality, narrative, and aesthetics respectively

### Problems/Solutions
- [ ] Setup GitHub issues and project
- [ ] ! Restructure repository according to system architecture
- [ ] Tool for generating NBT and JSON files from structures
- [ ] Centralised `World` representation > @tim
	- [ ] Different ways of map "perspective"
	- [ ] Different input/output > @victor
	- [ ] Generic design for use by public
