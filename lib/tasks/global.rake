namespace :data_setup do
  desc "Full data setup"
  task :full => [:environment, :trade_hubs, :regions, :load_all_items, :blueprints_setup, :stations]
end

namespace :data_compute do
  desc "Full prices recomputation"
  task :full => [:environment, :trade_hubs_prices, :get_orders]
end

namespace :data_compute do
  desc "Full prices recomputation"
  task :full_daily => [:environment, :costs, :get_prices_history_update ]
end