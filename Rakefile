require 'bundler/setup'
$:.unshift File.expand_path('../lib', __FILE__)

COMPOSE_TEST = 'docker-compose.yml'

desc 'Construir Entorno'
task :up do
  compose('up', '--build', '-d')
end

desc 'Eliminar Entorno'
task :del do
  compose('down', '-v', '--rmi', 'all', compose: COMPOSE_TEST)
end

DOCKER_COMPOSE_TEST=COMPOSE_TEST
def compose(*arg, compose: DOCKER_COMPOSE_TEST)
  sh "docker compose -f #{compose} #{arg.join(' ')}"
end
