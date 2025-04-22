# DFK Automation

## Overview

DFK Automation is a Python-based bot designed to automate hero questing in [DefiKingdoms](https://game.defikingdoms.com) (DFK), a blockchain-based RPG game built on DFK Chain and Klaytn. Instead of manually sending heroes on quests through the game's GUI interface, this bot interacts directly with the blockchain using the same smart contracts that power the game, allowing for efficient management of multiple heroes.

## Features

- **Automated Questing**: Send heroes on quests automatically based on profession and stamina
- **Multi-Quest Support**: Handles various quest types:
  - Fishing
  - Foraging
  - Gardening
  - Mining
- **Level-based Quest Selection**: Optimizes quest selection based on hero profession levels
  - Level 0 (profession < 100)
  - Level 10 (profession >= 100)
- **Batch Processing**: Efficiently groups heroes for quest submission
- **Quest Completion**: Automatically claims rewards when quests are completed
- **Gardening Pool Distribution**: Intelligently distributes gardening heroes across available pools

## Requirements

- Python 3.6+
- Dependencies listed in `requirements.txt`:
  - dfktools==0.3.2
  - python-dotenv==1.0.0
  - web3==6.8.0

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/dfk-automation.git
   cd dfk-automation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with your private key:
   ```
   PRIVATE_KEY=your_private_key_here
   ```
   **Important**: Never share your private key. Keep your `.env` file secure and never commit it to version control.

## Usage

Run the main script to start the automation:

```bash
python main.py
```

The script will:
1. Load your heroes from the blockchain
2. Check hero stamina and profession
3. Send eligible heroes on appropriate quests
4. Complete any finished quests and collect rewards
5. Wait for 10 minutes before running again

## How It Works

### Architecture

The project is structured around specialized classes for different quest types:

- `Questing`: Base class that handles common questing functionality
- `Gardening`: Extends Questing with gardening-specific features
- `Mining`: Specializes in mining operations

### Questing Logic

1. **Hero Selection**: Heroes are filtered based on:
   - Profession matching the quest type
   - Minimum stamina requirements (25 by default)
   - Not currently on another quest

2. **Level Differentiation**: 
   - Heroes with profession level < 100 are sent on level 0 quests
   - Heroes with profession level >= 100 are sent on level 10 quests

3. **Batch Processing**:
   - Fishing/Foraging: Heroes are grouped in batches of up to 6
   - Gardening: Heroes are paired in groups of 2
   - Mining: Heroes are grouped in batches of exactly 6

4. **Quest Completion**:
   - The script checks for completed quests
   - Automatically claims rewards when quests are finished

### Gardening Specifics

Gardening quests require pairs of heroes assigned to specific pools. The `Gardening` class:
- Tracks which pools are already active
- Distributes new hero pairs across available pools using a round-robin algorithm
- Ensures optimal pool utilization

## Networks

The bot currently supports:
- **Crystalvale** (DFK Chain): Fully supported with all quest types
- **Serendale2** (Klaytn): Partial support (configuration may need updating)

## Configuration

Network configurations are stored in `utils/net.py` and include:
- RPC endpoints
- Contract addresses
- Quest type IDs

## Customization

To modify stamina requirements or other parameters, edit the corresponding values in `main.py`.

## Docker Support

The project includes Docker configuration for containerized deployment:

```bash
# Build the Docker image
docker build -t dfk-automation .

# Run the container
docker run -d --name dfk-bot --env-file .env dfk-automation
```

## Security Considerations

- Store your private key securely in the `.env` file
- Never share your private key
- Consider using a dedicated wallet with limited funds for automation

## Troubleshooting

If you encounter issues:
- Check your private key is correctly set in the `.env` file
- Verify you have sufficient gas tokens (JEWEL on DFK Chain, KLAY on Klaytn)
- Ensure your heroes have sufficient stamina for questing

## Disclaimer

This bot interacts with blockchain transactions that have real financial implications. Use at your own risk and start with small tests before committing significant resources.

## License

[MIT License](LICENSE)

## Acknowledgements

- [DFK Tools](https://github.com/0rtis/dfktools) for the underlying API integration
- The DefiKingdoms team for creating the game
