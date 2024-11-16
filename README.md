# Embedding API

This project provides a robust API for generating image and text embeddings using advanced machine learning models. It also supports vector search with MongoDB Atlas. Follow the steps below to set up and use the API.

---

## Setup

### 1. Install Dependencies

Run the following command in the project root to install the required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Start the API

Launch the server from the project root with:

```bash
uvicorn app.main:app --reload
```

### 3. Configure MongoDB Atlas for Vector Search

- The API uses **MongoDB Atlas Vector Search** for storing and querying embeddings.  
  Learn more: [MongoDB Atlas Vector Search Overview](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview/)
- Create a `.env` file in the project root and add the following variable:

  ```
  MONGODB_URI=<your-mongodb-uri>

  MODEL_NAME="llama3.2"
  ```

- After setting up MongoDB Atlas, you can use the vector search. In the folder `app/routes` run the following command:
  ```bash
  python vector_search.py
  ```

---

## API Endpoints

You can use tools like **Postman** or **Thunderbird** to make requests to the API.

### 1. Generate Image Embeddings

- **Endpoint:**  
  `POST http://127.0.0.1:8000/image-embeddings`

- **JSON Request Body:**

  ```json
  {
    "url": "https://res.cloudinary.com/djq3wujos/image/upload/v1731701231/fffdwrq8tyoupj16jysr.jpg"
  }
  ```

- **Response Example:**

  ```json
  {
    "embeddings": [...],
    "dimension": 512,
    "message": "Embeddings gerados com sucesso"
  }
  ```

---

### 2. Generate Text Embeddings

- **Endpoint:**  
  `POST http://127.0.0.1:8000/text-embeddings/`

- **JSON Request Body:**

  ```json
  {
    "text": "guitarra"
  }
  ```

- **Response Example:**

  ```json
  {
    "embeddings": [...],
    "dimension": 2048,
    "message": "Embeddings gerados com sucesso"
  }
  ```

---

### 3. Retrieve Embedding Metadata

- **Endpoint:**  
  `GET http://127.0.0.1:8000/info/embedding-meta`

- **Response Example:**

  ```json
  {
    "text_emb_dimension": 2048,
    "text_emb_model": "llama3.2:1b",
    "img_emb_dimension": 512,
    "img_emb_model": "ViT-B-16",
    "message": "success"
  }
  ```

---

### 4. Vector Search

- **Endpoint:**  
  `POST http://127.0.0.1:8000/vector-search`

- **JSON Request Body:**

  ```json
   {
    "queryVector": [...],
    "collection": "my_collection",
    "numCandidates": 3,
    "limit": 2
  }
  ```
- **Response Example:**

  ```json
  {
  "results": [
    {
      "object": "item1",
      "objectDescription": "Item description",
      "score": 0.85
    },
    {
      "object": "item2",
      "objectDescription": "Another item description",
      "score": 0.80
    }
  ],
  "message": "Vector search completed successfully",
  "num_results": 2
  }
  ```
---

## Requirements

### Text Embeddings

- The API uses **llama3.2:1b** for text embeddings.  
  Download the model from: [https://github.com/ollama/ollama](https://github.com/ollama/ollama)

### Image Embeddings

- The API uses **OpenCLIP ViT-B-16** for image embeddings.  
  Repository: [https://github.com/mlfoundations/open_clip](https://github.com/mlfoundations/open_clip)

---

## Notes

1. Ensure that all required models are downloaded and set up before running the API.
2. MongoDB Atlas must be configured with the appropriate URI in the `.env` file.
3. Use the provided endpoints to easily integrate embeddings into your applications.

Enjoy using the **Embedding API**!
