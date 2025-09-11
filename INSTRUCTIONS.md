## DOCKER

#### Q: I want to run a single Docker container from a Dockerfile. Just the backend. How do I do this?

1. Make sure you are in the `./backend` directory in the terminal:
   ```sh
   cd backend
   ```
2. Build the Docker image (the `.` at the end is required):
   ```sh
   docker build -t agile-backend .
   ```
   This command builds an image named `agile-backend` from the Dockerfile in the current directory.
3. Run the Docker container:
   ```sh
   docker run -p 5000:5000 agile-backend
   ```
   - The `-p 5000:5000` flag maps port 5000 on your machine to port 5000 in the container.
4. Done! Your backend should now be accessible at [http://localhost:5000](http://localhost:5000).

---

#### Q: I want to start the entire project!

1. Make sure you are in the project root directory in the terminal.
2. Run:
   ```sh
   docker-compose up
   ```
   - This requires a `docker-compose.yml` file in the root directory.
3. Done!

---

#### Q: I want to stop the containers from running, help!

- Run:
  ```sh
  docker-compose down
  ```
- You can also pause or delete containers via Docker Desktop (check the containers icon).