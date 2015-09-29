namespace :data_setup do
  desc "Full data setup"
  task :full => [:environment, :trade_hubs, :regions, 'price_history:init', :load_all_items, :blueprints_setup, :stations, :market_groups]
end

namespace :data_compute do
  namespace :full do
    desc "Full process - hourly"
    task :hourly => [:environment, 'min_prices:used' , :get_orders, :get_sales]

    desc "Full process - daily"
    task :daily => [:environment, 'price_history:update:all', :costs]
  end
end