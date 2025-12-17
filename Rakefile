require 'bundler/setup'
$:.unshift File.expand_path('../lib', __FILE__)

COMPOSE_TEST = 'docker-compose.yml'

desc 'Construir Entorno'
task :up do
  compose('up', '--build', '-d')
end

desc 'reiniciar entorno'
task :restart do
  compose('restart', compose: COMPOSE_TEST)
end

desc 'Eliminar Entorno'
task :del do
  compose('down', '-vv', '--rmi', 'all', compose: COMPOSE_TEST)
end

desc 'Order Service'
namespace :order do
  desc 'Order Service Shell'
  task :sh do
    compose('exec', 'order-service', 'bash')
  end

  desc 'Order Service TDD'
  task :tdd do
    compose('exec', 'order-service', 'pytest -vvv')
  end

  desc 'Order Service Crear y Aplicar Migracion'
  task :migrate, [:description]  do |_, args|
    compose('exec', 'order-service', "alembic revision --autogenerate -m '#{args.description}'")
    compose('exec', 'order-service', 'alembic upgrade head')
  end

  desc 'Monitorear salida Order Service'
  task :tail do
    compose('logs', '-f', '-n 50', 'order-service', compose: COMPOSE_TEST)
  end
end

desc 'Inventory Service'
namespace :inventory do
  desc 'Inventory Service TDD'
  task :tdd do
    compose('exec', 'inventory-service', 'pytest -vvv')
  end

  desc 'Inventory Service Shell'
  task :sh do
    compose('exec', 'inventory-service', 'bash')
  end

  desc 'Monitorear salida Inventory Service'
  task :tail do
    compose('logs', '-f', '-n 50', 'inventory-service', compose: COMPOSE_TEST)
  end
end

desc 'Payment Service'
namespace :pay do
  desc 'Payment Service TDD'
  task :tdd do
    compose('exec', 'payment-service', 'pytest -vvv')
  end

  desc 'Payment Service Shell'
  task :sh do
    compose('exec', 'payment-service', 'bash')
  end

  desc 'Monitorear salida Payment Service'
  task :tail do
    compose('logs', '-f', '-n 50', 'payment-service', compose: COMPOSE_TEST)
  end
end

desc 'Notification Service'
namespace :noti do
  desc 'Notification Service TDD'
  task :tdd do
    compose('exec', 'notification-service', 'pytest -vvv')
  end

  desc 'Notification Service Shell'
  task :sh do
    compose('exec', 'notification-service', 'bash')
  end

  desc 'Monitorear salida Notification Service'
  task :tail do
    compose('logs', '-f', '-n 50', 'notification-service', compose: COMPOSE_TEST)
  end
end

DOCKER_COMPOSE_TEST=COMPOSE_TEST
def compose(*arg, compose: DOCKER_COMPOSE_TEST)
  sh "docker compose -f #{compose} #{arg.join(' ')}"
end
