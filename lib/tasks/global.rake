namespace :data_setup do
  desc "Full data setup"
  task :full => [:environment, :create_first_user, :trade_hubs, :eve_objects, :blueprints_setup, :stations]
end

namespace :data_compute do
  desc "Full prices recomputation"
  task :full => [:environment, :refresh_components_costs, :refresh_items_costs, :trade_hubs_prices]
end