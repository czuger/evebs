namespace :data_setup do
  desc "Full data setup"
  task :full => [:environment, :trade_hubs, :regions, 'price_history:init', :load_all_items, :blueprints_setup, :stations]
end

namespace :data_compute do
  namespace :full do
    desc "Full process - hourly"
    task :hourly => [:environment, 'min_prices:used' , :get_orders, :get_sales]

    desc "Full process - daily"
    task :daily => [:environment, 'get_prices_history:update', :costs]
  end
end