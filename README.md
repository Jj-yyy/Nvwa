

# Nvwa: Race Survival Simulation Game

Nvwa is a turn-based strategy mini-game that simulates "creation" and "civilization evolution." Players protect their tribe's population over 5 rounds by rolling dice, allocating resources, and facing random natural events. At the end, different civilization endings are triggered based on your choices.

## How to Play
1. **Roll the Dice**: Click the dice button each round. The dice will randomly show a number from 1–6, which is your resource points for the round.
2. **Allocate Resources**: Choose one of the three resources—Food, Defense, or Technology. All resource points for the round are added to your chosen resource.
3. **Random Events**: At the end of each round, a random event (e.g., Harvest +2, Flood -2) is automatically triggered, affecting the population.
4. **Ending Judgment**: After 5 rounds, the game automatically determines the civilization ending based on your resources and population.

## Core Variables
| Variable      | Meaning                    | Initial Value |
| ------------  | ------------------------- | ------------- |
| Food          | Stability & growth         | 0             |
| Defense       | Disaster resistance        | 0             |
| Technology    | Civilization advancement   | 0             |
| Population    | Current living population  | 5             |

## Random Events
| Event Name    | Effect         | Population Change |
| ------------- | -------------- | ----------------- |
| Drought       | Population -   | -1                |
| Harvest       | Population +   | +2                |
| Winter        | Population -   | -1                |
| Flood         | Population -   | -2                |
| Fertile Land  | Population +   | +2                |

## Ending Rules
### Basic Endings
1. Population = 0 → Extinction
2. 0 < Population ≤ 7 → Primitive Eternity
3. 7 < Population ≤ 10 → Population Prosperity
4. Population > 10 → Population Overload

### Special Civilization Endings
- Agricultural Age: Food ≥ 8 and Technology ≥ 5, and 7 < Population ≤ 10
- Scientific Revolution: Food ≥ 10, 3 ≤ Defense < 5, Technology ≥ 8, and 7 < Population ≤ 10
- Utopia: Food ≥ 10 and Technology ≥ 10, and 7 < Population ≤ 10
- AI Crisis: Food ≥ 8, Defense ≥ 25, Technology ≥ 10, and Population ≥ 10

## Project Structure
```
main.py           # Main game program
static/           # Static resources
  UI/             # UI assets
  游戏结局png/     # Ending images
  随机事件gif/     # Random event GIFs
  骰子/           # Dice images
```

## Requirements
- Python 3.x
- Dependencies: pygame, pillow

## How to Run
1. Install Python 3 and dependencies:
  ```powershell
  pip install pygame pillow
  ```
2. Run the main program:
  ```powershell
  python main.py
  ```

## License
For learning and personal use only.
