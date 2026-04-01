.PHONY: help up down restart logs status shell-backend shell-db reset clean

COMPOSE = docker-compose -f docker/docker-compose.yml

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

up: ## Démarre tous les services
	$(COMPOSE) up -d

down: ## Arrête tous les services
	$(COMPOSE) down

restart: ## Redémarre tous les services
	$(COMPOSE) restart

logs: ## Affiche les logs en temps réel
	$(COMPOSE) logs -f

logs-backend: ## Affiche les logs du backend uniquement
	$(COMPOSE) logs -f backend

status: ## Affiche l'état des conteneurs
	$(COMPOSE) ps

shell-backend: ## Ouvre un shell dans le conteneur backend
	$(COMPOSE) exec backend /bin/bash

shell-db: ## Ouvre un shell MySQL
	$(COMPOSE) exec db mysql -u root -proot medtech_patients

build: ## Reconstruit les images Docker
	$(COMPOSE) build --no-cache

reset: ## Arrête, supprime les volumes et redémarre (remet la BDD à zéro)
	$(COMPOSE) down -v
	$(COMPOSE) up -d

clean: ## Supprime les conteneurs, images et volumes orphelins
	$(COMPOSE) down --rmi local --volumes --remove-orphans
