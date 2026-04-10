local:
	docker-compose -f docker-compose.local.yaml up --build

prod:
	docker-compose -f docker-compose.prod.yaml up --build

clean:
	docker system prune -a

drop_all_data:
	docker-compose exec redis redis-cli FLUSHALL
	docker-compose exec db psql -U postgres -d budget_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;"
	docker-compose exec minio sh -c "mc alias set local http://localhost:9000 minio_access_key minio_secret_key 2>/dev/null || true; mc rm --recursive --force local/uploads 2>/dev/null || true"
	docker-compose exec bot alembic upgrade head
	@echo "[SUCCESS] All data cleared!"
