COMPOSE = docker-compose

# Services
build:
	$(COMPOSE) build

start:
	$(COMPOSE) up -d

stop:
	$(COMPOSE) down

restart:
	$(COMPOSE) down && $(COMPOSE) up

logs:
	$(COMPOSE) logs -f

agents-start:
	@echo "🚀 Starting agents in background..."
	nohup docker-compose exec smarthotel_backend python manage.py run_agents > logs/agents.log 2>&1 & \
	echo $$! > .agents_pid && echo "🆗 Agents started with PID $$!"

# Stops the background agent process
agents-stop:
	@echo "🛑 Stopping agents..."
	@if [ -f .agents_pid ]; then \
		kill -SIGINT `cat .agents_pid` && rm .agents_pid && echo "✅ Agents stopped."; \
	else \
		echo "⚠️  No agent PID file found."; \
	fi

# View the logs
agents-logs:
	@tail -f logs/agents.log
