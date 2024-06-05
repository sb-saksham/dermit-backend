# DermIT: Multi-Modal AI Powered Dermatological Application

⚡ Experience Dermatological Diagnosis on your Finger Tips 💪

## OVERVIEW

DermIT is a multi-modal AI-based dermatological diagnosis application that targets the global dermatological burden and aims to provide the real-world experience of a dermatologist with just a few simple clicks. The app can be used for diagnosis as well as for studying dermatology. For this project, I have collaborated with multiple dermatologists to identify and address the issues that come with such mobile applications. It pairs computer vision and retrieval augmentation generation (RAG) to capture visually seen symptoms as well as unseen symptoms such as medical history, hereditary conditions, and so on. This approach ensures DermIT never misses any symptoms and diagnoses them as accurately as possible.

## WORK FLOW

The workflow starts with the user answering multiple-choice questionnaire based on their lifestyle to form a wider picture, followed by uploading images to the computer vision (CV) model. The CV model detects symptoms rather than the disease itself. Inputs from the survey and the CV model are then fed to the RAG model. The RAG provides a chat interface in which the user can explain their concern just as they would explain it to a physician, thus producing a comprehensive response, including the identified disease, a thorough explanation, charts, possible lifestyle changes, precautions, and advice.

## TECHNICAL ASPECT

1. For the frontend, I have leveraged `React.Js` with modern UI solutions such as `Tailwind CSS` and `NextUI`. To utilize `websockets`, I have used `react-use-websockets` in the frontend.
2. Since there was no image dataset for the task at hand, I gathered the images by scraping them from the web, which consists of around 4000 images, and labeled them manually using `Roboflow`. Finally, transfer learning was applied to the state-of-the-art `YoloV8x`, and the desired computer vision model was prepared.
3. For the RAG, I have utilized `LangChain` to build a performant retriever `agent` powered by `gpt-3.5-turbo` paired with multiple tools to handle various user inputs. The RAG also has a memory element to store the conversation's context in memory. For semantic searching and vector storage, `FAISS` is used, in which data is converted into embedding chunks based on metadata.
4. In the backend, `Django REST Framework` is used to handle API requests based on users. Images of the users are stored in `AWS S3`, acting as the CDN for the app; diagnoses,  including conversations, and other data are stored in the `SQLite` database. The backend uses websockets for real-time chatting (for RAG) using `Django Channels` with `Redis` as the message broker.  

## HOW TO RUN?

### Step 1: Fork and Clone the Repo

To run the project you would need to fork and clone both the [frontend](https://github.com/Taha0229/dermit-react-frontend) and the [backend](https://github.com/Taha0229/dermit-backend). It is advised to first fork then clone the repo, so that you can also make changes in your own copy of the project
`git clone [forked repo url]`

### Step 2: Setup the Backend

The app works as intended however, Since the app is under heavy development a lot of designing patterns are limited to streamline the process .  

A. Right now, only redis is configured in the docker container. This is due to the fact that some python dependencies that are used in the development Windows OS are not present in the Docker's Linux OS moreover redis is not directly supported in the windows.
B. The file structure is vague due to the complex integration of various components such as multiple vector store, chunking strategy, multi-modal integration and on-the go Django's model preparation during the development process (and much more).

1. Create super user(s) using the following command to access the app from the frontend.
`python manage.py createsuperuser`
This is a required command because the frontend doesn't support sign up at the moment but it supports logging in

2. Migrate the database
`python manage.py makemigrations` followed by  
`python manage.py migarte`

3. Due to the described issues, you have to run two command to launch the server:
`python manage.py runserver`  
`docker compose up` or `docker compose up -d` (make sure you have installed docker and started the docker engine)

Finally, the server should be up and running without any error, unless you try to access the backend in the browser. You can go to `localhost:8000/admin` for admin panel and `localhost:8000/api/` to view all the possible api routes.

### Step 3: Setup the Frontend

Setting up the frontend is quite simple, just run the following command-
`npm run dev`  
Even though all the routes are mapped in the Nav bar, still you can investigate the `app.jsx` file and the file structure to determine the routes as due to development process few testing routes may be existing but are not mapped.  
Click on `Diagnose` in the Nav bar to start the diagnosis process.  

## PROJECT BACKGROUND & DEVELOPER'S NOTE

This project took a lot of intensive research to figure out correct and effective implementation. The research involved analyzing other AI powered apps in the domain of health-care in India. In conclusion we came to know that there were no multi-modal apps for diagnosing dermatology featuring computer vision and text-generation. Later, we also approached few dermatologists and medical students from top medical institutes to discuss and improve the solution, and since then DermIT is under active development.

I personally tested multiple frameworks and methodology to built the desired RAG model but always encountered with a new set of problem as soon as the previous one was resolve.  
I have built RAG pipelines from scratch without orchestration framework but it performed very badly. I also tried building a model with `Llama-index` which worked exceptionally well but I faced a lot of issues. Around February 10th I started using `Llama-index` and it happened to be the same day when they released a major update changing the entire code base and implementations, the document was not updated and any tutorial was useless. I was left with the only option i.e. to look for the implementation in the codebase itself.  
For this I used a quantized `Mistral-7b-instruct-v1` (16 bit float) as the LLM, a custom hugging face embedding model- `sentence-transformers/multi-qa-mpnet-base-cos-v1` with a support of 768 dimensional dense embedding. `LangChain` wrappers were used to build the frontend of the RAG such as prompt, output parser and setting up the embedding model while everything related to the raw data pipelines and LLM was managed by using `Llama-index`.  
Everything was working fine but I was interested in LangChain's brand new `LCEL` (stable). I believed at that time, LangChain was offering much more control and features over the overall RAG development, be it function calling, memory units, tools and routes, LangChain was ahead of Llama-index and hence I shifted to LangChain (however right now Llama-index introduced almost all the listed features).  
With developing each feature I get ideas for few more and therefore, the developing cycle is gonna go a bit long.  
