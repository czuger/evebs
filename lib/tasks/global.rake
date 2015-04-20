namespace :data_setup do
  desc "Full data setup"
  task :full => [:environment, :create_first_user, :trade_hubs, :eve_objects, :blueprints_setup, :stations]
end