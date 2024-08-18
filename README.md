
# AI Traditional Chinese Medicine Consultation System

This project is an AI-based Traditional Chinese Medicine (TCM) consultation system called **L AI**. The system integrates various modules to process health data, interact with users, and generate responses based on AI models. The project leverages multiple Python libraries, including LangChain, OpenCC, and Google API.

## Project Structure

```bash
.
├── .env                    # Environment variables (API keys, etc.)
├── chain.py                # Main pipeline and process control
├── data.py                 # Data loading and handling
├── main.py                 # Entry point for the AI consultation system
├── model.py                # AI model initialization and configuration
├── prompt.py               # Chatbot prompt template
├── requirements.txt        # Python dependencies
├── health_data/
│   ├── 123456202404301505.csv   # Example health data file
│   ├── 202404301434.csv         # Example health data file
│   ├── data_template.csv        # CSV template for new user data
│   └── test_user.csv            # Test user data
└── sources/
    ├── functions.py             # Utility functions for information extraction and processing
    └── zh_tw_convert.py         # Chinese text conversion (Simplified to Traditional)
```

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:

   - Copy the `.env` file in the root directory and fill in the necessary details (e.g., `GOOGLE_API_KEY`).

## Usage

1. **Health Data Handling**: 
   - Health data is stored in the `health_data/` folder. You can create new health data CSV files based on the `data_template.csv` file.
   - The `data.py` module handles data loading and processing. It dynamically generates models and loads CSV files.

2. **Model Initialization**: 
   - The AI model is configured in `model.py`. It uses the Google Generative AI API for generating responses. Ensure that your API key is correctly set in the `.env` file.

3. **Chatbot Interaction**:
   - The main interaction logic is defined in `main.py`. This file initializes the chatbot, manages the chat history, and processes user inputs using the `chain.py` pipeline.

4. **Text Conversion**:
   - `zh_tw_convert.py` handles text conversion between Simplified and Traditional Chinese. This is especially useful when dealing with multilingual inputs.

## Examples

- **Starting the System**:
  To start the AI consultation system, run the following command:

  ```bash
  python main.py
  ```

- **Generating New Health Data**:
  To create a new CSV file for a user, use the `createCSV(username)` function in `data.py`.

## Customization

- **Chatbot Prompt**:
  You can modify the chatbot's behavior by editing the prompt template in `prompt.py`.

- **Pipeline Customization**:
  The `chain.py` file contains the main pipeline logic. You can modify or extend it by adding new steps or changing the data flow between different modules.

## Contributing

If you wish to contribute to this project, please submit a pull request with your proposed changes. Ensure that your code follows best practices and includes appropriate tests.

## License

This project is licensed under the [MIT License](LICENSE).
