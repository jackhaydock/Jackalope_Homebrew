# Jackalope Homebrew
Homebrew collection for [5e.tools](https://5e.tools) for my 5e campaign settings.

My items will have the following sources/labels making it easy to identify them within 5eTools:
- Main Collection
  - **Jackalope: General/J:General**: General collection of stuff.
  - **Jackalope: Antithesis Subclasses/J:Antithesis**: Subclasses themed around being the opposite of class steroetypes.
  - **Jackalope: Ash and Snow/J:AnS**: Stuff for my viking themed setting, Ash and Snow.
  - **Jackalope: Awakened Energy Warlock/J:Energy**: Warlock with sentient energy as patron, themed around choice of damage type.
  - **Jackalope: Battlemage Fighter/J:Battlemage**: Revised Eldritch Knight with more choices in spell lists and other features.
  - **Jackalope: Beastkin/J:Beastkin**: Various animalistic races and subraces. Also includes some racial feats.
  - **Jackalope: Blessings of the Drunkard/J:Drunk**: Boons from a hedonistic god, such as Dionysus.
  - **Jackalope: Children of Morrigan/J:Morrigan**: Stuff for my celtic folklore themed setting, Children of Morrigan.
  - **Jackalope: Custom Dragons/J:Dragons**: Rules and examples for building custom dragons.
  - **Jackalope: Darkweaver Warlock/J:Darkweaver**: Spider/underdark themed warlock. Can control the battlefield with webs, poison and fear.
  - **Jackalope: Dragon Warlock/J:Dragonlock**: Dragon themed warlock, summons spectral dragon head.
  - **Jackalope: Feast Domain Cleric/J:Feast**: Cleric of the feast, can make spell storing food.
  - **Jackalope: Firearms/J:Firearms**: Firearms from matchlock to flintlock. Also includes accessories, mods, feats and invocations.
  - **Jackalope: Gaian/J:Gaian**: Races spawned from typically unliving minerals, such as ice, magma and gems.
  - **Jackalope: Hivemind Warlock/J:Hivemind**: Warlock subclass, patron is a hivemind.
  - **Jackalope: Kobolds/J:Kobolds**: Extra kobold subraces, may get feats, item and statblocks later.
  - **Jackalope: Pact of the Shield/J:Shieldlock**: Pact boon for warlock themed around defence and a summonable shield.
  - **Jackalope: Portalist Class/J:Portalist**: Portal themed half-caster class.
  - **Jackalope: Runestones/J:Runestones**: Transferable enchantments for magic items.
  - **Jackalope: Tattoos/J:Tattoos**: Magic tattoos.
  - **Jackalope: Temporal Subclasses/J:Temporal**: Time themed subclasses for multiples classes.
  - **Jackalope: The Sea of Cyranos/J:Cyranos**: Stuff for my classic greek themed setting, The Sea of Cyranos.
  - **Jackalope: The Skies of Caligos/J:Caligos**: Stuff for my steampunk themed setting, The Skies of Caligos.
  - **Jackalope: Vermin Rogue/J:Vermin**: Rogue with a familiar, that can pick locks and sneak attack.
  - **Jackalope: Wheelchair/J:Wheelchair**: Wheelchair and upgrades (inspired by Combat Wheelchair but simplified).
  - **Jackalope: Wild Magic/J:Wild**: Wild magic and chaos themed subclasses and items.
- Extra Collection (generally not allowed for actual play in my games unless stated otherwise)
  - **Jackalope: Partypack/J:Partypack**: Memes and character specific stuff.
  - **Jackalope: The Caféy/J:Caféy**: A travelling café in the feywild serving bizare food and drinks.
- Legacy Collection (generally not allowed for actual play in my games unless stated otherwise)
  - **Jackalope: Portalist Class (Legacy)/J:Portalist**: Older version of the Portalist, likely even more broken.

If inline links don't work, it may be refering to something that is in one of the other sources that you don't have.

## How to Import

#### 5eTools
1. Goto https://5e.tools/managebrew.html (or a mirror if you prefer)

2. Click "Load from URL" and copy/paste some or all of following URLs:
 - Main Collection (multiple sources of stuff generally allowed in my games): `https://raw.githubusercontent.com/jackhaydock/Jackalope_Homebrew/master/merged_jsons/jackalope_main.json`
 - Extra Collection (contains memes and character specific items): `https://raw.githubusercontent.com/jackhaydock/Jackalope_Homebrew/master/merged_jsons/jackalope_extra.json`
 - Legacy Collection (old stuff, not recommended): `https://raw.githubusercontent.com/jackhaydock/Jackalope_Homebrew/master/merged_jsons/jackalope_legacy.json`
 - Full Collection (all the above in one file): `https://raw.githubusercontent.com/jackhaydock/Jackalope_Homebrew/master/merged_jsons/jackalope_all.json`
 - You can also get the URLs to raw json files inside `source_jsons` if you want specific collections.
3. You should then see items in their respective lists.

In theory, you only need to import each URL once and then simply click Update in future to get any future changes, which I recommend doing frequently as I update this repo frequently.

*NOTE: Some class features (like fighting styles and pact boons), may not appear on the class pages, be sure to check the [optional features](https://5e.tools/optionalfeatures.html) page.*

#### Plutonium/Foundry
1. In foundry, when selecting a source for importing select "Custom URL" and paste the URLs above.

OR (as gamemaster)

1. Download/Clone/Pull the json file(s).
2. In Foundry, open the Plutonium Config Editor and navigate to Import->Additional Homebrew Files.
3. Enter the path to the json file(s).
4. When selecting sources to import you, and your players, should see a source (usually alongside a blue tankard icon), select them and you'll see the items.
