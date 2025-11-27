docker build -t bbu:latest .
docker stop bbu-container
docker rm bbu-container
docker run --name bbu-container \
	-v /home/Shey/Backboard/backboard-updater/logs:/app/logs \
	-e SUPABASE_URL=<SUPABASE_URL> \
	-e SUPABASE_KEY=<SUPABASE_KEY> \
	-it bbu:latest