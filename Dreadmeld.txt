{{Anomaly}}
{{Spoiler}}
{{infobox main|entity
| name = Dreadmeld
| image = Dreadmeld.png
| description = A gargantuan amalgamation of dozens of smaller fleshbeasts linked together by a loosely shared central nervous system. It uses its massive claws to dig tunnels through solid rock. Fleshbeast dreadmelds are rarely seen above ground, instead sheltering in caverns built from living flesh. They share a psychic connection with the flesh used to create their burrow.
<!-- Base Stats -->
| type = Entity
| type2 = Advanced
| flammability = 1.25
<!-- Containment -->
| gets cold containment bonus = true
| base escape interval MTB days = 60
<!-- Pawn Stats -->
| combatPower = 650
| movespeed = 1.5
| healthscale = 10
| bodysize = 5
| diet = none
| lifespan = 50
| trainable = None
| psychic sensitivity = 0.5
| toxic resistance = 0.8
| min comfortable temperature = -40
| max comfortable temperature = 60
| body = Dreadmeld
<!-- Production -->
| meatname = Twisted meat
| meatyield = 70
<!-- Combat -->
| attack1label = left spike
| attack1labelNoLocation = spike
| attack1type = Stab
| attack1dmg = 14
| attack1cool = 2
| attack1alwaysTreatAsWeapon = true
| attack1part = LeftSpike
| attack2label = right spike
| attack2labelNoLocation = spike
| attack2type = Stab
| attack2dmg = 14
| attack2cool = 2
| attack2alwaysTreatAsWeapon = true
| attack2part = RightSpike
| attack3label = head
| attack3type = Blunt
| attack3dmg = 3
| attack3cool = 2
| attack3part = HeadAttackTool
| attack3ensureLinkedBodyPartsGroupAlwaysUsable = true
| attack3chancefactor = 0.2
| destroyyield = 3 {{Icon Small|Shard|24}} + 30 {{Icon Small|Bioferrite|24}}
<!-- Technical -->
| defName = Dreadmeld
| label = dreadmeld
<!-- Other -->
<!--
| deathAction Class="DeathActionProperties_Divide" = 
| divideBloodFilthCountRange = 3~4| /divideBloodFilthCountRange = 
| dividePawnKindAdditionalForced = Toughspike, Trispike, Bulbfreak
| renderTree = Dreadmeld
| lifeStageAges: def = EntityFullyFormed
| compClass = CompDreadmeld
| Class="CompProperties_LetterOnRevealed" = 
| label = Dreadmeld released
| text = You've discovered a fleshbeast dreadmeld! This mammoth creature seems to be made up of dozens of smaller fleshbeasts.<br /><br />It appears to have some psychic connection to the fleshmass that supports this cavern. Killing it may destabilize the entire cave system.
| letterDef = ThreatBig
| ThingDef Name="BaseFleshbeast" ParentName="BasePawn" Abstract="True" = 
| thingClass = Pawn
| category = Pawn
| selectable = true
| containedPawnsSelectable = true
| containedItemsSelectable = true
| tickerType = Normal
| altitudeLayer = Pawn
| useHitPoints = false
| hasTooltip = true
| drawHighlight = true
| tradeability = None
| hiddenWhileUndiscovered = true
| renderTree = Misc
| thinkTreeMain = Fleshbeast
| thinkTreeConstant = FleshbeastConstant
| intelligence = ToolUser
| specificMeatDef = Meat_Twisted
| overrideShouldHaveAbilityTracker = true
| disableIgniteVerb = true
| canOpenFactionlessDoors = false
| needsRest = false
| hasGenders = false
| bloodDef = Filth_Blood
| bloodSmearDef = Filth_BloodSmear
| fleshType = Fleshbeast
| isImmuneToInfections = true
| bleedRateFactor = 0.5
| hediffGiverSets = Fleshbeast
| corpseHiddenWhileUndiscovered = true
| inspectorTabs = ITab_Pawn_Health, MayRequire="Ludeon.RimWorld.Anomaly" = ITab_Entity, ITab_Pawn_Log
| compClass = CompAttachBase
| Class="CompProperties_InspectString" = 
| compClass = CompInspectStringEmergence
| inspectString = Emerged from {SOURCEPAWN_labelShort}.
| drawGUIOverlay = true
-->
}}
The '''dreadmeld''' is an [[entity]] added by the [[Anomaly DLC]]. It is the largest of the [[fleshbeast]]s and can be considered the "boss battle" of the [[pit gate]]. 

== Occurrence == 
Dreadmelds appear inside of [[pit gate]] undercaves. Every undercave has a single dreadmeld residing somewhere inside. It will always be completely enclosed by [[fleshmass]] walls, preventing it from being accessed until it is freed. When approaching the chamber containing a dreadmeld for the first time, a unique "Squirming sounds" warning letter appears, similar to when first approaching an [[ancient danger]]:
{{Quote|As <PAWN NAME> draws near the fleshmass here, they sense a heavy writhing and throbbing from under its warm surface. Some huge living entity is hidden behind the wall of flesh.|"Squirming sounds" letter}}

== Summary ==
Dreadmelds are highly durable entities with an extremely slow movement speed. While their powerful melee attack is roughly equivalent to a [[warg]]'s, their primary threat comes in the form of their unique ability to spawn smaller [[fleshbeast]]s as it takes damage. For every 200 total damage the dreadmeld takes from any source, 100-300 [[Raid points|combat power]] worth of fleshbeasts will spawn around it, distributed randomly within a 5-tile radius. This will result in semi-random distributions of {{Icon Small|Fingerspike}} [[fingerspike]]s, {{Icon Small|Toughspike}} [[toughspike]]s, and {{Icon Small|Trispike}} [[trispike]]s. Dreadmelds additionally also spawn 1-3 fingerspikes the first time they take damage.

Dreadmelds have a [[body size]] of 5, making them one of the largest creatures in the game.

Like [[ghoul]]s, dreadmelds possess rapid regeneration. They heal at the same rate, but can regenerate a total of 350 HP/day instead of the ghoul's smaller 100 HP/day.

When a dreadmeld dies, it splits into a fingerspike, a toughspike, and a {{Icon Small|Bulbfreak}} [[bulbfreak]], leaving behind three [[shard]]s in the process. The pit gate it resides within will then begin to destabilize. After 12 hours, it will close permanently; any items or pawns remaining in the undercave are then irretrievably destroyed. The undercave will remain stable indefinitely as long as the dreadmeld remains alive.

Dreadmelds are immune to all psychic lances ([[psychic shock lance|shock]], [[psychic insanity lance|insanity]], [[biomutation lance|biomutation]]).

Dreadmelds cannot be captured for containment. They will always die on being downed.

== Analysis ==
The dreadmeld is slow and lumbering, only chasing the closest attacker. Barraging it with gunfire while having another pawn [[kiting|kite]] it is the safest way to deal with it. Handling its additional spawns is a top priority; damaging the dreadmeld too quickly, without focusing on the additional fleshbeasts, can rapidly create a critical mass that will overrun even experienced [[Melee]] fighters through sheer numbers alone. Consider clearing any lingering fleshmass from the route you plan to take it through, as the additional cover can block shots that would otherwise damage the fleshbeasts.

[[Melee block|Melee blocking]] a dreadmeld is possible, but requires setup and preparation. Because of the random scattering of new fleshbeasts, it is plausible that they will land behind your ranged fighters and immediately engage them at close range, meaning that close-range weapons such as [[chain shotgun]]s or [[heavy SMG]]s can make a significant difference for crowd control. Stunning tools, like [[disruptor flare pack]]s or [[vertigo pulse]], {{RoyaltyIcon}} can be very effective in reducing the overall damage taken. Constructing fortifications in advance rather than simply fighting in the undercave's natural layout is also a significant boon.

Whatever strategy is used to face a dreadmeld, ensuring a quick and controlled kill on the first engagement is vital. Because of its impossible regeneration, a dreadmeld left for long enough will quickly heal any damage done to it; a routed attack may inflict no lasting attrition and simply result in wasted time and injured pawns.

Pit gates contain numerous [[flesh sack]]s that can yield bionic or archotech [[artificial body part]]s, and they also often possess numerous [[ore]]s such as [[compacted steel]] that can be useful to the colony. Ensure that you don't engage the dreadmeld until you are ready to close the pit gate. When you are ready, double-check to ensure there isn't anything you might be forgetting, and make sure that your pawns have a clear and safe path to the exit that they can promptly follow once the dreadmeld is dispatched (and its shards collected).

Optionally, if you want to use the pit cave for some other purpose, don't unleash the dreadmeld in the first place. When you identify the chamber it's contained within, make a note of where it is and leave it in peace until you're ready to leave.

Like all fleshbeasts, the dreadmeld is not immune to [[toxic buildup]], and will eventually die and cause the cave to collapse if exposed to polluted terrain for an extended duration. Dumping a large number of [[toxic wastepack]]s{{BiotechIcon}} into a [[pit gate]] and allowing them to decay or intentionally destroying them (e.g: setting them on fire), will spread [[pollution]]{{BiotechIcon}} though the undercave, even through solid rock, which will eventually reach the dreadmeld's location. Doing so can allow a colony to close a pit gate with a minimal amount of exploration and no combat. Due to dreadmelds being vulnerable to toxic buildup, pit gates can not be used indefinitely as wastepack dumping sites, although they may work for a long time. Players who keep a pit gate open for an extended time for wastepack dumping should an eye on the spread of pollution relative to the dreadmeld's chamber.

== Health ==
{{Animal Health Table|Dreadmeld}}
{{Pawn Attack Table}}

== Version history == 
* [[Anomaly DLC]] Release - Added.

{{Nav|entity|wide}}
[[Category: Entities]]
[[Category: Fleshbeasts]]