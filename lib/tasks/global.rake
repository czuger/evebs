namespace :data_setup do
  desc "Full data setup"
  task :full => [:environment, :trade_hubs, :eve_objects, :blueprints_setup, :stations]
end

namespace :data_compute do
  desc "Full prices recomputation"
  task :full => [:environment, :retrieve_all_components_costs, :recompute_all_items_costs, :trade_hubs_prices, :get_orders]
end