namespace :data_setup do
  desc 'Full data setup'
  task :full => [:environment, :trade_hubs, :regions, 'price_history:init', :update_all_items, :blueprints_setup, :stations, :market_groups]
end

namespace :data_compute do
  namespace :full do
    desc 'Full process - hourly'
    # task :hourly => [:environment, :min_prices, :get_orders, :prices_advices, :jita_margins ]
    # task :hourly => [:environment, :print_time, :min_prices, :prices_advices, :jita_margins, :print_time ]
    task :hourly => [:environment, :print_time, :prices_advices, :print_time ]

    desc 'Full process - daily'
    task :weekly => [:environment, 'data_setup:update_all_items', :eve_markets_histories, :compute_prices_history_average, :costs]
  end
end