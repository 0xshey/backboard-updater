docker build -t bbu:latest .
docker stop bbu-container
docker rm bbu-container
docker run --name bbu-container \
	-e SUPABASE_URL=<SUPABASE_URL> \
	-e SUPABASE_KEY=<SUPABASE_KEY> \
	-it bbu:latest